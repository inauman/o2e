"""
Service for managing secure memory storage with auto-clearing.
"""

import threading
from typing import Dict, Any, Optional

class SecureMemoryManager:
    """
    Manages secure storage of sensitive data in memory with auto-clearing.
    """
    
    def __init__(self, timeout: int = 60):
        """
        Initialize the secure memory manager.
        
        Args:
            timeout: Number of seconds before auto-clearing (default: 60)
        """
        self.timeout = timeout
        self._storage = {}
        self._timers = {}
        self._lock = threading.Lock()
    
    def store(self, key: str, value: str) -> None:
        """
        Store a value securely with auto-clearing after timeout.
        
        Args:
            key: The key to store the value under
            value: The value to store
        """
        with self._lock:
            # Cancel any existing timer
            if key in self._timers and self._timers[key] is not None:
                self._timers[key].cancel()
            
            # Store the value
            self._storage[key] = value
            
            # Set a timer to clear the value
            self._timers[key] = threading.Timer(self.timeout, self.clear, args=[key])
            self._timers[key].daemon = True
            self._timers[key].start()
    
    def get(self, key: str) -> Optional[str]:
        """
        Retrieve a stored value.
        
        Args:
            key: The key to retrieve
            
        Returns:
            The stored value, or None if not found
        """
        with self._lock:
            return self._storage.get(key)
    
    def clear(self, key: str = None) -> None:
        """
        Clear stored values.
        
        Args:
            key: The specific key to clear, or None to clear all
        """
        with self._lock:
            if key is not None:
                if key in self._storage:
                    del self._storage[key]
                if key in self._timers:
                    if self._timers[key] is not None:
                        self._timers[key].cancel()
                    del self._timers[key]
            else:
                # Clear all values
                for timer_key in list(self._timers.keys()):
                    if self._timers[timer_key] is not None:
                        self._timers[timer_key].cancel()
                self._storage.clear()
                self._timers.clear()
    
    def extend_timeout(self, key: str) -> bool:
        """
        Extend the timeout for a stored value.
        
        Args:
            key: The key to extend timeout for
            
        Returns:
            True if the timeout was extended, False if the key was not found
        """
        with self._lock:
            if key not in self._storage:
                return False
            
            # Get the current value
            value = self._storage[key]
            
            # Store it again (which resets the timer)
            self.store(key, value)
            
            return True 