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

Add the following entry in your `configuration.yaml` (quick example):

```yaml
light:
  - platform: sp110e
    mac: AF:00:10:01:C8:AF # Replace with your MAC address (required)
```

Full list of options (full example)

```yaml
light:
  - platform: sp110e
    mac: AF:00:10:01:C8:AF # Replace with your MAC address (required)
    name: SP110E # Device name for UI (optional, default: SP110E)
    ic_model: UCS1903 # Circuit model (optional)
    sequence: GRB # Color sequence (optional)
    pixels: 60 # Number of LED pixels (optional)
    strict: false # If true, you will get an error trying to operate with offline device (optional, default: false)
    add_effects: # Custom effects in addition to built-in modes (optional)
      - name: New Year # Custom name (required)
        mode: 2 # (optional)
        speed: 75 # (optional)
      - name: Sunset
        color: [255, 64, 0]
        brightness: 255
```

## FAQ

Q: I'm getting error `[Errno 2] No such file or directory` when running Home Assistant from Docker container

A: Add this volume to your container: `/var/run/dbus/:/var/run/dbus/:z`

## Development

### Create new release

⚠️ Do not forget to update `requirements` section in [manifest.json](custom_components/sp110e/manifest.json)

Push changes to 'main' branch following [Conventional Commits](https://www.conventionalcommits.org/en/v1.0.0/).

## Useful links

- [SP110E Python Library](https://github.com/roslovets/SP110E)

## ⭐️ Show your support

Give a star if this project helped you.
