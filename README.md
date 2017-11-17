Overview
=========

lort's purpose is to make testing LEDE/OpenWRT easy.

Requirements:

- A VLAN-capable switch
- A Linux PC to drive test loads
- At least 2 routers with fresh installs of Lede/OpenWRT

To use:

1. Set up a switch with a trunk port (going to your test pc), and untagged 
vlans on ports to be used for testing. I personally use vlan ids that match 
port ids.
2. Plug your hardware into the ports assigned to the vlan.
3. `lort setup eth0 5-10`
4. `lort discover` <-TODO
5. ????
6. Profit


TODO
----

`lort discover` should jump on all network namespaces listed by `lort list`,
and autodetect uplink or downlink, device type, firmware version and uniqueness.

potential features:
 
`lort upgrade`: build and install firmware for all discovered devices, given a specified source dir.

`lort test`: start up pre-defined servers, execute a test, etc.

`lort configure`: configure a network.
