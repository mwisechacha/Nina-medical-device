import asyncio
import numpy as np
import matplotlib.pyplot as plt
from bleak import BleakScanner, BleakClient

# Replace with your BLE device's MAC address and characteristic UUID
DEVICE_ADDRESS = "XX:XX:XX:XX:XX:XX"  # e.g., "12:34:56:78:9A:BC"
CHARACTERISTIC_UUID = "xxxxxxxx-xxxx-xxxx-xxxx-xxxxxxxxxxxx"  # e.g., "0000ffe1-0000-1000-8000-00805f9b34fb"

received_data = []

def handle_data(sender, data):
    # Append received bytes to the list
    received_data.append(data)
    print(f"Received data chunk of size {len(data)}")

async def main():
    print("Scanning for BLE devices...")
    devices = await BleakScanner.discover()
    for d in devices:
        print(d)

    print(f"Connecting to device {DEVICE_ADDRESS}...")
    async with BleakClient(DEVICE_ADDRESS) as client:
        print(f"Connected: {client.is_connected}")

        await client.start_notify(CHARACTERISTIC_UUID, handle_data)
        print("Listening for data... Press Ctrl+C to stop.")
        try:
            await asyncio.sleep(10)  # Listen for 10 seconds (adjust as needed)
        except KeyboardInterrupt:
            print("Stopped by user.")
        await client.stop_notify(CHARACTERISTIC_UUID)

    # Combine all received data
    all_data = b''.join(received_data)
    # Convert to numpy array (adjust dtype to match your sensor, e.g., np.float32)
    signal = np.frombuffer(all_data, dtype=np.float32)
    print("Received signal shape:", signal.shape)

    # Frequency analysis (FFT)
    freq_spectrum = np.fft.fft(signal)
    freq_magnitude = np.abs(freq_spectrum)
    freqs = np.fft.fftfreq(signal.size, d=1.0)  # Adjust d=1.0 to your sample rate

    # Save spectrum as plot
    plt.figure(figsize=(10, 4))
    plt.plot(freqs, freq_magnitude)
    plt.title("Ultrasonic Signal Frequency Spectrum")
    plt.xlabel("Frequency (Hz)")
    plt.ylabel("Magnitude")
    plt.savefig("ultrasonic_spectrum.png")
    print("Saved frequency spectrum as ultrasonic_spectrum.png")

    # Save signal for AI model
    np.save("ultrasonic_signal.npy", signal)
    print("Saved signal as ultrasonic_signal.npy")

if __name__ == "__main__":
    asyncio.run(main())