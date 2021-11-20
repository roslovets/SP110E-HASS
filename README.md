# SP110E Home Assistant Integration

Control SP110E RGB LED BLE Controller from Home Assistant

### Supported features:

- Turn on/off
- Set brightness
- Set color
- Set white color brightness
- Select mode
- Configure device

### Installation

Copy `custom_components/sp110e` folder to `<config_dir>/custom_components/`.

Add the following entry in your `configuration.yaml` (example):

```yaml
light:
  - platform: sp110e
    mac: AF:00:10:01:C8:AF # Replace with your MAC address (required)
    name: SP110E # Device name for UI (optional, default: SP110E)
    ic_model: UCS1903 # Circuit model (optional)
    sequence: GRB # Color sequence (optional)
    pixels: 60 # Number of LED pixels (optional)
```

## FAQ

Q: I'm getting error `[Errno 2] No such file or directory` when running Home Assistant from Docker container

A: Add this volume to your container: `/var/run/dbus/:/var/run/dbus/:z`

## Development

### Create new release

Push changes to 'main' branch following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## Useful links

- [SP110E Python Library](https://github.com/roslovets/SP110E)
