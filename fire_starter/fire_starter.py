import concurrent.futures

import concurrent.futures
from collections import defaultdict
from typing import Callable, Any, Dict, Set


class FireStarter:
    """
    A class to manage event listeners and dispatch events to them.

    Attributes:
        listeners (Dict[str, Set[Callable]]): A dictionary that maps event names to their corresponding listeners.
        listener_priorities (Dict[str, Dict[Callable, int]]): A dictionary that stores listener priorities for each event.
    """

    def __init__(self) -> None:
        """
        Initialize the FireStarter class.
        """
        self.listeners: Dict[str, Set[Callable]] = defaultdict(set)
        self.listener_priorities: Dict[str, Dict[Callable, int]] = defaultdict(dict)

    def add_listener(self, event_name: str, listener: Callable, priority: int = 0) -> 'FireStarter':
        """
        Add a listener function to an event.

        Args:
            event_name (str): The name of the event to attach the listener to.
            listener (Callable): The listener function to be called when the event is dispatched.
            priority (int, optional): The priority of the listener. Higher values execute first. Defaults to 0.

        Returns:
            FireStarter: The FireStarter instance for method chaining.
        """
        self.listeners[event_name].add(listener)
        self.listener_priorities[event_name][listener] = priority
        return self

    def remove_listener(self, event_name: str, listener: Callable) -> 'FireStarter':
        """
        Remove a listener function from an event.

        Args:
            event_name (str): The name of the event from which to remove the listener.
            listener (Callable): The listener function to be removed.

        Returns:
            FireStarter: The FireStarter instance for method chaining.
        """
        self.listeners[event_name].discard(listener)
        self.listener_priorities[event_name].pop(listener, None)
        return self

    def fire(self, event_name: str, *args: Any, **kwargs: Any) -> 'FireStarter':
        """
        Dispatch an event to its listeners.

        Args:
            event_name (str): The name of the event to dispatch.
            *args: Variable length argument list for the listener functions.
            **kwargs: Arbitrary keyword arguments for the listener functions.

        Returns:
            FireStarter: The FireStarter instance for method chaining.
        """
        listeners = self.listeners[event_name]
        listeners_with_priority = sorted(listeners, key=lambda l: self.listener_priorities[event_name][l], reverse=True)

        # Run listeners concurrently using ThreadPoolExecutor
        with concurrent.futures.ThreadPoolExecutor() as executor:
            futures = [executor.submit(self.execute_listener, listener, *args, **kwargs) for listener in listeners_with_priority]
            concurrent.futures.wait(futures)

        return self

    def execute_listener(self, listener: Callable, *args: Any, **kwargs: Any) -> None:
        """
        Execute a listener function with the given arguments.

        Args:
            listener (Callable): The listener function to be executed.
            *args: Variable length argument list for the listener function.
            **kwargs: Arbitrary keyword arguments for the listener function.
        """
        try:
            listener(*args, **kwargs)
        except Exception as e:
            print(f"Error in listener execution: {e}")

    def event(self, event_name: str, priority: int = 0) -> Callable:
        """
        Decorator to add a listener to an event with an optional priority.

        Args:
            event_name (str): The name of the event to attach the listener to.
            priority (int, optional): The priority of the listener. Higher values execute first. Defaults to 0.

        Returns:
            Callable: The decorator function to attach the listener to the event.
        """
        def decorator(listener: Callable) -> Callable:
            self.add_listener(event_name, listener, priority=priority)
            return listener
        return decorator

    def get_all_events(self) -> Set[str]:
        """
        Get a set of all unique event names registered in the FireStarter.

        Returns:
            Set[str]: A set containing all event names.
        """
        return set(self.listeners.keys())