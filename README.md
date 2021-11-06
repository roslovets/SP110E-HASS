# SP110E Home Assistant Integration

Control SP110E RGB LED BLE Controller from Home Assistant

### Supported features:

- Turn on/off

### Installation

Copy files to `<config_dir>/custom_components/sp110e/`.

Add the following entry in your `configuration.yaml`:

```yaml
light:
  - platform: sp110e
    mac: AF:00:10:01:C8:AF # Replace with your MAC address
```

## FAQ

Q: I'm getting error `[Errno 2] No such file or directory` when running Home Assistant from Docker container

A: Add this volume to your container: `/var/run/dbus/:/var/run/dbus/:z`

## Useful links

- [SP110E Python Library](https://github.com/roslovets/SP110E)
