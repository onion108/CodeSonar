from conductor import Conductor
from sensors import SystemSensor


def main():
    print("Starting Code Sonar - Ambient Edition...")
    print("Press Ctrl+C to stop.")

    sensor = SystemSensor()
    conductor = Conductor(sensor)

    try:
        conductor.start()
    except KeyboardInterrupt:
        print("\nStopping Code Sonar...")
    except Exception as e:
        print(f"\nError: {e}")
        # SCAMP might need fluid synth.
        print(
            "Note: If you hear no sound, ensure you have a MIDI output device or Fluidsynth installed/configured."
        )


if __name__ == "__main__":
    main()
