# Example usage:
from typing import Any

from fire_starter import FireStarter

fire_starter = FireStarter()


@fire_starter.event('event_fired', priority=2)
def on_event_fired(message: str) -> None:
    print(f"Event fired: {message}")


@fire_starter.event('data_received', priority=1)
def on_data_received(data: Any) -> None:
    print(f"Data received: {data}")


# Dispatch multiple events in a single line using threading
fire_starter.fire('event_fired', "Hello, World!").fire('data_received', [1, 2, 3])

# Remove a listener and dispatch another event using threading
fire_starter.remove_listener('event_fired', on_event_fired)
fire_starter.fire('event_fired', "This won't be printed.")

# Get all events
all_events = fire_starter.get_all_events()
print(all_events)  # Output: {'event_fired', 'data_received'}
