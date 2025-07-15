import voluptuous as vol

# Card schema allows arbitrary keys so users can pass any card options
CARD_SCHEMA = vol.Schema(
    {vol.Required("type"): str}, extra=vol.ALLOW_EXTRA
)

ROOM_SCHEMA = vol.Schema(
    {
        vol.Required("name"): str,
        vol.Optional("order"): vol.Coerce(int),
        vol.Optional("layout"): vol.In(["horizontal", "vertical"]),
        vol.Optional("cards", default=[]): [CARD_SCHEMA],
        vol.Optional("conditions"): [str],
        vol.Optional("hidden", default=False): bool,
    },
    extra=vol.ALLOW_EXTRA,
)

CONFIG_SCHEMA = vol.Schema(
    {
        vol.Optional("auto_discover", default=False): bool,
        vol.Optional("header"): {
            vol.Required("title"): str,
            vol.Optional("logo"): str,
            vol.Optional("show_time", default=False): bool,
        },
        vol.Optional("sidebar"): [
            {
                vol.Required("name"): str,
                vol.Optional("icon"): str,
                vol.Optional("view"): str,
                vol.Optional("condition"): str,
            }
        ],
        vol.Optional("layout"): {
            vol.Optional("strategy", default="masonry"): str
        },
        vol.Optional("theme", default="auto"): vol.In(["light", "dark", "auto"]),
        vol.Optional("load_lovelace_cards", default=False): bool,
        vol.Optional("resources", default=[]): [
            {
                vol.Required("url"): str,
                vol.Required("type"): str,
            }
        ],
        vol.Optional("rooms", default=[]): [ROOM_SCHEMA],
    }
)
