"""
   Copyright 2025 Y22 Laboratories SA

   Licensed under the Apache License, Version 2.0 (the "License");
   you may not use this file except in compliance with the License.
   You may obtain a copy of the License at

       http://www.apache.org/licenses/LICENSE-2.0

   Unless required by applicable law or agreed to in writing, software
   distributed under the License is distributed on an "AS IS" BASIS,
   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
   See the License for the specific language governing permissions and
   limitations under the License.
"""

import json
import logging
from typing import Any, Dict, Optional
from fastapi import FastAPI, Request, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field
from pydantic_settings import BaseSettings
import httpx
import uvicorn

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    """Application settings using Pydantic Settings"""
    slack_webhook_url: Optional[str] = Field(default=None, description="Slack webhook URL for sending notifications")
    slack_channel: Optional[str] = Field(default=None, description="Slack channel to send notifications to")
    slack_username: str = Field(default="CloudEvent Bot", description="Username for Slack messages")
    slack_icon_emoji: str = Field(default=":cloud:", description="Emoji icon for Slack messages")
    slack_data_limit: int = Field(default=256, description="Maximum characters for event data in Slack messages")
    
    class Config:
        env_file = ".env"
        env_prefix = ""

class SlackMessage(BaseModel):
    """Slack message payload model"""
    text: str
    channel: Optional[str] = None
    username: str = "CloudEvent Bot"
    icon_emoji: str = ":cloud:"

# Initialize settings
settings = Settings()

# Log configuration on startup
logger.info(f"Starting EOEPCA Slack notification function")
logger.info(f"Slack webhook configured: {'Yes' if settings.slack_webhook_url else 'No'}")
if settings.slack_channel:
    logger.info(f"Default destination channel: {settings.slack_channel}")
else:
    logger.info("No default destination channel configured")

app = FastAPI(title="Knative CloudEvent Function", version="1.0.0")

async def send_to_slack(cloudevent_data: Dict[str, Any], headers: Dict[str, str]) -> bool:
    """Send CloudEvent data to Slack webhook"""
    try:
        # Check if Slack is configured
        if not settings.slack_webhook_url:
            logger.info("Slack webhook URL not configured, skipping Slack notification")
            return False
        
        # Extract CloudEvent information
        ce_headers = {k: v for k, v in headers.items() if k.startswith('ce-')}
        
        # Format message for Slack
        message_text = "🌩️ *CloudEvent Received*\n\n"
        
        if ce_headers:
            message_text += "*CloudEvent Headers:*\n"
            for key, value in ce_headers.items():
                clean_key = key.replace('ce-', '').replace('-', ' ').title()
                message_text += f"• *{clean_key}:* `{value}`\n"
            message_text += "\n"
        
        if cloudevent_data:
            # Limit data field to specified character limit
            data_json = json.dumps(cloudevent_data, indent=2)
            if len(data_json) > settings.slack_data_limit:
                truncated_data = data_json[:settings.slack_data_limit - 3] + "..."
                message_text += "*Event Data (truncated):*\n"
                message_text += f"```json\n{truncated_data}\n```"
                message_text += f"\n_Data truncated to {settings.slack_data_limit} characters_"
            else:
                message_text += "*Event Data:*\n"
                message_text += f"```json\n{data_json}\n```"
        
        # Create Slack message payload
        slack_payload = SlackMessage(
            text=message_text,
            channel=settings.slack_channel,
            username=settings.slack_username,
            icon_emoji=settings.slack_icon_emoji
        )
        
        # Send to Slack webhook
        async with httpx.AsyncClient() as client:
            response = await client.post(
                settings.slack_webhook_url,
                json=slack_payload.model_dump(exclude_none=True),
                timeout=10.0
            )
            response.raise_for_status()
            
        logger.info("Successfully sent CloudEvent to Slack")
        return True
        
    except httpx.HTTPError as e:
        logger.error(f"HTTP error sending to Slack: {e}")
        return False
    except Exception as e:
        logger.error(f"Unexpected error sending to Slack: {e}")
        return False

@app.get("/health")
async def health_check():
    """Health check endpoint for Kubernetes liveness probe"""
    return {"status": "healthy", "message": "Function is running"}

@app.get("/ready")
async def readiness_check():
    """Readiness check endpoint for Kubernetes readiness probe"""
    return {"status": "ready", "message": "Function is ready to receive requests"}

@app.post("/")
async def handle_cloudevent(request: Request):
    """
    Handle incoming CloudEvents of any type.
    Prints the event details to the console and sends them to Slack.
    """
    try:
        # Get headers
        headers = dict(request.headers)
        
        # Get body
        body = await request.body()
        
        # Try to parse as JSON if possible
        try:
            json_body = json.loads(body) if body else {}
        except json.JSONDecodeError:
            json_body = {"raw_body": body.decode("utf-8", errors="ignore")}
        
        # Extract CloudEvent headers
        ce_headers = {k: v for k, v in headers.items() if k.startswith('ce-')}
        
        # Log the complete CloudEvent information
        logger.info("=" * 60)
        logger.info("RECEIVED CLOUDEVENT")
        logger.info("=" * 60)
        
        if ce_headers:
            logger.info("CloudEvent Headers:")
            for key, value in ce_headers.items():
                logger.info(f"  {key}: {value}")
        
        logger.info("Request Headers:")
        for key, value in headers.items():
            logger.info(f"  {key}: {value}")
        
        logger.info("Request Body:")
        logger.info(json.dumps(json_body, indent=2))
        
        logger.info("=" * 60)
        
        # Send to Slack
        slack_success = await send_to_slack(json_body, headers)
        
        # Return success response
        response_content = {
            "message": "CloudEvent received and processed successfully",
            "slack_notification": "sent" if slack_success else ("skipped" if not settings.slack_webhook_url else "failed")
        }
        
        return JSONResponse(
            status_code=200,
            content=response_content
        )
        
    except Exception as e:
        logger.error(f"Error processing CloudEvent: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error processing CloudEvent: {str(e)}")

@app.get("/")
async def root():
    """Root endpoint with basic information"""
    return {
        "message": "Knative CloudEvent Function",
        "version": "1.0.0",
        "endpoints": {
            "health": "/health",
            "readiness": "/ready",
            "cloudevents": "POST /"
        }
    }

if __name__ == "__main__":
    # Run the application
    uvicorn.run(
        "func:app",
        host="0.0.0.0",
        port=8080,
        log_level="info",
        access_log=True
    )
