# BillaMusic/utils/exceptions.py
"""
Custom exceptions for the BillaMusic project.
These exceptions are used to handle errors gracefully across the application,
particularly in voice chat and streaming operations.
"""

class AssistantErr(Exception):
    """Base exception for general errors in the BillaMusic assistant."""
    def __init__(self, message: str):
        self.message = message
        super().__init__(self.message)


class VoiceChatError(AssistantErr):
    """Raised when there is an issue with voice chat operations (e.g., joining, leaving)."""
    def __init__(self, message: str, chat_id: int = None):
        self.chat_id = chat_id
        message = f"Voice chat error: {message}" + (f" in chat {chat_id}" if chat_id else "")
        super().__init__(message)


class StreamError(AssistantErr):
    """Raised when there is an issue with streaming audio or video."""
    def __init__(self, message: str, stream_type: str = None):
        self.stream_type = stream_type
        message = f"Stream error: {message}" + (f" for {stream_type} stream" if stream_type else "")
        super().__init__(message)


class DownloadError(AssistantErr):
    """Raised when there is an issue downloading media files."""
    def __init__(self, message: str, url: str = None):
        self.url = url
        message = f"Download error: {message}" + (f" for URL {url}" if url else "")
        super().__init__(message)


class ConfigError(AssistantErr):
    """Raised when there is an issue with configuration or session strings."""
    def __init__(self, message: str):
        super().__init__(f"Configuration error: {message}")


class DatabaseError(AssistantErr):
    """Raised when there is an issue with database operations."""
    def __init__(self, message: str, chat_id: int = None):
        self.chat_id = chat_id
        message = f"Database error: {message}" + (f" in chat {chat_id}" if chat_id else "")
        super().__init__(message)
