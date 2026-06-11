
SRV_MAPPING: dict[str, list[tuple[str, str]]] = {
    # --- Active Directory / Microsoft (high-value enterprise recon) ---
    "active_directory": [
        ("ldap", "tcp"),
        ("ldaps", "tcp"),
        ("gc", "tcp"),               # Global Catalog
        ("gc", "udp"),
        ("kerberos", "tcp"),
        ("kerberos", "udp"),
        ("kerberos-master", "tcp"),
        ("kerberos-master", "udp"),
        ("kerberos-adm", "tcp"),
        ("kpasswd", "tcp"),
        ("kpasswd", "udp"),
        ("kca", "tcp"),
        ("ntds", "tcp"),
        ("msft-gc", "tcp"),
        ("msft-gc-ssl", "tcp"),
    ],

    # --- Mail (Exchange autodiscover is a frequent finding) ---
    "mail": [
        ("autodiscover", "tcp"),     # Exchange / Outlook
        ("autoconfig", "tcp"),
        ("imap", "tcp"),
        ("imaps", "tcp"),
        ("pop3", "tcp"),
        ("pop3s", "tcp"),
        ("smtp", "tcp"),
        ("smtps", "tcp"),
        ("submission", "tcp"),
        ("submissions", "tcp"),      # RFC 8314 implicit-TLS submission
    ],

    # --- XMPP / chat federation ---
    "xmpp": [
        ("xmpp-client", "tcp"),
        ("xmpp-server", "tcp"),
        ("xmpps-client", "tcp"),
        ("xmpps-server", "tcp"),
        ("jabber", "tcp"),
        ("jabber-client", "tcp"),
        ("jabber-server", "tcp"),
    ],

    # --- SIP / VoIP / WebRTC ---
    "voip": [
        ("sip", "tcp"),
        ("sip", "udp"),
        ("sip", "tls"),
        ("sips", "tcp"),
        ("sipfederationtls", "tcp"),  # Skype for Business / Lync edge
        ("sipinternaltls", "tcp"),
        ("sipexternaltls", "tcp"),
        ("h323cs", "tcp"),
        ("h323ls", "udp"),
        ("h323rs", "udp"),
        ("stun", "tcp"),
        ("stun", "udp"),
        ("stuns", "tcp"),
        ("turn", "tcp"),
        ("turn", "udp"),
        ("turns", "tcp"),
        ("iax", "udp"),
    ],

    # --- Calendaring / contacts (DAVish) ---
    "dav": [
        ("caldav", "tcp"),
        ("caldavs", "tcp"),
        ("carddav", "tcp"),
        ("carddavs", "tcp"),
    ],

    # --- Web / file / generic transport ---
    "web_file": [
        ("http", "tcp"),
        ("https", "tcp"),
        ("www", "tcp"),
        ("www-http", "tcp"),
        ("ftp", "tcp"),
        ("ftps", "tcp"),
        ("sftp-ssh", "tcp"),
        ("ssh", "tcp"),
        ("telnet", "tcp"),
        ("nfs", "tcp"),
        ("smb", "tcp"),
        ("cifs", "tcp"),
        ("afpovertcp", "tcp"),
        ("webdav", "tcp"),
        ("webdavs", "tcp"),
    ],

    # --- AAA / directory / time ---
    "infra": [
        ("radius", "tcp"),
        ("radius", "udp"),
        ("radsec", "tcp"),
        ("radiustls", "tcp"),
        ("diameter", "tcp"),
        ("diameter", "sctp"),
        ("diameters", "tcp"),
        ("ntp", "udp"),
        ("nntp", "tcp"),
        ("whois", "tcp"),
        ("finger", "tcp"),
        ("syslog", "udp"),
        ("snmp", "udp"),
    ],

    # --- Federation / modern protocols ---
    "federation": [
        ("matrix", "tcp"),
        ("matrix-fed", "tcp"),       # RFC-style Matrix server discovery
        ("nicovideo", "tcp"),
    ],

    # --- DNS-SD / Bonjour / zeroconf service discovery ---
    "dns_sd": [
        ("services._dns-sd", "udp"),  # meta-query: enumerate advertised types
        ("ipp", "tcp"),
        ("ipps", "tcp"),
        ("printer", "tcp"),
        ("pdl-datastream", "tcp"),
        ("scanner", "tcp"),
        ("airplay", "tcp"),
        ("raop", "tcp"),
        ("airport", "tcp"),
        ("googlecast", "tcp"),
        ("spotify-connect", "tcp"),
        ("hap", "tcp"),               # HomeKit Accessory Protocol
        ("homekit", "tcp"),
        ("workstation", "tcp"),
        ("device-info", "tcp"),
        ("sleep-proxy", "udp"),
        ("rfb", "tcp"),               # VNC
        ("adisk", "tcp"),             # Time Machine
        ("daap", "tcp"),              # iTunes
        ("dacp", "tcp"),
    ],

    # --- Game / community servers ---
    "games": [
        ("teamspeak", "udp"),
        ("ts3", "udp"),
        ("mumble", "tcp"),
        ("wesnoth", "tcp"),
        ("starcraft", "tcp"),
        ("minecraft", "tcp"),
    ],

    # --- Misc / less common but worth probing ---
    "misc": [
        ("vlmcs", "tcp"),             # KMS volume activation
        ("kms", "tcp"),
        ("imps-server", "tcp"),
        ("ocsp", "tcp"),
        ("crl", "tcp"),
        ("dns", "tcp"),
        ("dns", "udp"),
        ("doh", "tcp"),
        ("dot", "tcp"),
        ("git", "tcp"),
        ("svn", "tcp"),
        ("rsync", "tcp"),
        ("ldap-admin", "tcp"),
        ("backup", "tcp"),
        ("collab-edge", "tls"),       # Cisco Expressway / Jabber MRA
        ("cisco-uds", "tcp"),         # Cisco UC user data service
        ("cuplogin", "tcp"),
        ("ciscowtp", "tcp"),
    ]
}