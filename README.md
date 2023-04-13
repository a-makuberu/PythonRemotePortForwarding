# SSH Tunnel with Remote Port Forwarding

This Python script uses the Paramiko library to establish an SSH tunnel for port forwarding. It can be used to securely forward traffic from a remote server to a local machine through an encrypted connection.

## Features

- Configurable settings (SSH server, username, password, remote bind port, forward host, forward port, and SSH log file location)
- Settings can be provided directly within the code or loaded from a JSON file
- Logs connection and forwarding events with timestamps
- Handles multiple connections in parallel using threads

## Requirements

- Python 3.x
- Paramiko library

To install Paramiko, run:

```sh
pip install paramiko
```

## Usage

1. Set your desired SSH server and port forwarding settings in the `settings` dictionary within the script or in a JSON file. Make sure to set the `SETTING_IN_CODE` variable to `True` if you want to use the settings defined in the script, or `False` if you want to load them from a JSON file.

2. Run the script:

```sh
python RemotePortForwarding.py
```

The script will establish an SSH connection and set up port forwarding. It will run indefinitely, accepting and handling multiple connections in parallel until interrupted.

To stop the script, press `Ctrl+C`.

## Contributing

Contributions are welcome! If you have any suggestions for improvements or bug fixes, please submit a pull request or open an issue on the project's repository.

## License

This project is licensed under the MIT License. For more information, see the [LICENSE](./LICENSE) file in the project's repository.

