from typing import List

import requests

from backend.data.block import Block, BlockCategory, BlockOutput, BlockSchema
from backend.data.model import BlockSecret, SchemaField, SecretField

BLOTATO_API_BASE = "https://api.blotato.com"


def _blotato_headers(api_key: str) -> dict:
    return {
        "blotato-api-key": api_key,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }


class PublishToBlotatoBlock(Block):
    """Publishes a post to social media platforms via Blotato."""

    class Input(BlockSchema):
        api_key: BlockSecret = SecretField(
            key="blotato_api_key",
            description="Your Blotato API key. Get it from Settings > API Access at https://my.blotato.com.",
            placeholder="Enter your Blotato API key",
        )
        content: str = SchemaField(
            description="The text content of the post",
            placeholder="Enter your post content",
        )
        platforms: List[str] = SchemaField(
            description="List of platform identifiers to publish to (e.g. ['twitter', 'linkedin', 'instagram'])",
            placeholder="['twitter']",
        )
        media_urls: List[str] = SchemaField(
            default=[],
            description="Optional list of media URLs to attach to the post",
            placeholder="[]",
        )
        scheduled_at: str | None = SchemaField(
            default=None,
            description="Optional ISO 8601 datetime to schedule the post (e.g. '2026-03-15T10:00:00Z'). If not set, publishes immediately.",
            placeholder="2026-03-15T10:00:00Z",
        )

    class Output(BlockSchema):
        post_id: str = SchemaField(description="The ID of the created Blotato post")
        status: str = SchemaField(
            description="The status of the post (e.g. 'published', 'scheduled')"
        )
        error: str = SchemaField(
            description="Error message if the post creation failed"
        )

    def __init__(self):
        super().__init__(
            id="a1f5c3e7-8b2d-4f6a-9e0c-1d3b5a7f9e2c",
            input_schema=PublishToBlotatoBlock.Input,
            output_schema=PublishToBlotatoBlock.Output,
            description="Publishes a post to social media platforms via Blotato.",
            categories={BlockCategory.SOCIAL},
            test_input={
                "api_key": "test_blotato_key",
                "content": "Hello from AutoGPT!",
                "platforms": ["twitter"],
                "media_urls": [],
                "scheduled_at": None,
            },
            test_output=[
                ("post_id", "post_abc123"),
                ("status", "published"),
            ],
            test_mock={
                "publish_post": lambda *args, **kwargs: {
                    "id": "post_abc123",
                    "status": "published",
                }
            },
        )

    def publish_post(
        self,
        api_key: str,
        content: str,
        platforms: List[str],
        media_urls: List[str],
        scheduled_at: str | None,
    ) -> dict:
        payload: dict = {
            "content": content,
            "platforms": platforms,
        }
        if media_urls:
            payload["mediaUrls"] = media_urls
        if scheduled_at:
            payload["scheduledAt"] = scheduled_at

        response = requests.post(
            f"{BLOTATO_API_BASE}/v2/posts",
            headers=_blotato_headers(api_key),
            json=payload,
        )
        response.raise_for_status()
        return response.json()

    def run(self, input_data: Input, **kwargs) -> BlockOutput:
        try:
            result = self.publish_post(
                input_data.api_key.get_secret_value(),
                input_data.content,
                input_data.platforms,
                input_data.media_urls,
                input_data.scheduled_at,
            )
            yield "post_id", result.get("id", "")
            yield "status", result.get("status", "unknown")
        except requests.RequestException as e:
            yield "error", f"Network error publishing to Blotato: {str(e)}"
        except Exception as e:
            yield "error", f"Error publishing to Blotato: {str(e)}"


class UploadBlotatorMediaBlock(Block):
    """Uploads a media file to Blotato for use in posts."""

    class Input(BlockSchema):
        api_key: BlockSecret = SecretField(
            key="blotato_api_key",
            description="Your Blotato API key.",
            placeholder="Enter your Blotato API key",
        )
        media_url: str = SchemaField(
            description="The URL of the media file to upload",
            placeholder="https://example.com/image.png",
        )

    class Output(BlockSchema):
        media_id: str = SchemaField(
            description="The Blotato media ID for use in posts"
        )
        hosted_url: str = SchemaField(
            description="The hosted URL of the uploaded media"
        )
        error: str = SchemaField(
            description="Error message if the upload failed"
        )

    def __init__(self):
        super().__init__(
            id="b2e6d4f8-9c3e-4a7b-8f1d-2e4c6b8a0d3f",
            input_schema=UploadBlotatorMediaBlock.Input,
            output_schema=UploadBlotatorMediaBlock.Output,
            description="Uploads media to Blotato for use in social media posts.",
            categories={BlockCategory.SOCIAL},
            test_input={
                "api_key": "test_blotato_key",
                "media_url": "https://example.com/image.png",
            },
            test_output=[
                ("media_id", "media_xyz789"),
                ("hosted_url", "https://cdn.blotato.com/media/xyz789.png"),
            ],
            test_mock={
                "upload_media": lambda *args, **kwargs: {
                    "id": "media_xyz789",
                    "url": "https://cdn.blotato.com/media/xyz789.png",
                }
            },
        )

    def upload_media(self, api_key: str, media_url: str) -> dict:
        response = requests.post(
            f"{BLOTATO_API_BASE}/v2/media",
            headers=_blotato_headers(api_key),
            json={"url": media_url},
        )
        response.raise_for_status()
        return response.json()

    def run(self, input_data: Input, **kwargs) -> BlockOutput:
        try:
            result = self.upload_media(
                input_data.api_key.get_secret_value(),
                input_data.media_url,
            )
            yield "media_id", result.get("id", "")
            yield "hosted_url", result.get("url", "")
        except requests.RequestException as e:
            yield "error", f"Network error uploading media to Blotato: {str(e)}"
        except Exception as e:
            yield "error", f"Error uploading media to Blotato: {str(e)}"


class RepurposeContentBlotatorBlock(Block):
    """Repurposes existing content into new formats for different platforms using Blotato."""

    class Input(BlockSchema):
        api_key: BlockSecret = SecretField(
            key="blotato_api_key",
            description="Your Blotato API key.",
            placeholder="Enter your Blotato API key",
        )
        source_url: str = SchemaField(
            description="The URL of the source content to repurpose (e.g. a YouTube video, blog post, tweet)",
            placeholder="https://youtube.com/watch?v=...",
        )
        target_platform: str = SchemaField(
            description="The target platform format (e.g. 'twitter', 'linkedin', 'instagram')",
            placeholder="twitter",
        )

    class Output(BlockSchema):
        resolution_id: str = SchemaField(
            description="The ID of the content repurposing job"
        )
        content: str = SchemaField(
            description="The repurposed content text"
        )
        status: str = SchemaField(
            description="The status of the repurposing job"
        )
        error: str = SchemaField(
            description="Error message if repurposing failed"
        )

    def __init__(self):
        super().__init__(
            id="c3f7e5a9-0d4f-4b8c-9a2e-3f5d7c9b1e4a",
            input_schema=RepurposeContentBlotatorBlock.Input,
            output_schema=RepurposeContentBlotatorBlock.Output,
            description="Repurposes content from one platform to another using Blotato's AI.",
            categories={BlockCategory.SOCIAL},
            test_input={
                "api_key": "test_blotato_key",
                "source_url": "https://youtube.com/watch?v=test123",
                "target_platform": "twitter",
            },
            test_output=[
                ("resolution_id", "res_abc123"),
                ("content", "Repurposed content for Twitter"),
                ("status", "completed"),
            ],
            test_mock={
                "create_source_resolution": lambda *args, **kwargs: {
                    "id": "res_abc123",
                },
                "get_source_resolution": lambda *args, **kwargs: {
                    "id": "res_abc123",
                    "status": "completed",
                    "content": "Repurposed content for Twitter",
                },
            },
        )

    def create_source_resolution(
        self, api_key: str, source_url: str, target_platform: str
    ) -> dict:
        response = requests.post(
            f"{BLOTATO_API_BASE}/v2/source-resolutions-v3",
            headers=_blotato_headers(api_key),
            json={
                "sourceUrl": source_url,
                "targetPlatform": target_platform,
            },
        )
        response.raise_for_status()
        return response.json()

    def get_source_resolution(self, api_key: str, resolution_id: str) -> dict:
        response = requests.get(
            f"{BLOTATO_API_BASE}/v2/source-resolutions-v3/{resolution_id}",
            headers=_blotato_headers(api_key),
        )
        response.raise_for_status()
        return response.json()

    def run(self, input_data: Input, **kwargs) -> BlockOutput:
        import time

        try:
            create_result = self.create_source_resolution(
                input_data.api_key.get_secret_value(),
                input_data.source_url,
                input_data.target_platform,
            )
            resolution_id = create_result.get("id", "")
            yield "resolution_id", resolution_id

            # Poll for completion (max 60 seconds)
            for _ in range(12):
                result = self.get_source_resolution(
                    input_data.api_key.get_secret_value(),
                    resolution_id,
                )
                status = result.get("status", "")
                if status == "completed":
                    yield "content", result.get("content", "")
                    yield "status", "completed"
                    return
                if status == "failed":
                    yield "error", result.get("error", "Repurposing failed")
                    return
                time.sleep(5)

            yield "status", "timeout"
            yield "error", "Content repurposing timed out after 60 seconds"

        except requests.RequestException as e:
            yield "error", f"Network error with Blotato: {str(e)}"
        except Exception as e:
            yield "error", f"Error repurposing content via Blotato: {str(e)}"
