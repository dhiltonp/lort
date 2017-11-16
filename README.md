Overview
=========

XXX's purpose is to make testing Lede/OpenWRT easy.

Requirements:

- A VLAN-capable switch
- A Linux PC to drive test loads
- At least 2 routers with fresh installs of Lede/OpenWRT

To use:

1. Set up a switch with a trunk port (going to your test pc), and untagged 
vlans on ports to be used for testing. I personally use vlan ids that match 
port ids.
2. Plug your hardware into the ports assigned to the vlan.
3. `xxx setup eth0 5-10`
4. `xxx discover`
5. ????
6. Profit
