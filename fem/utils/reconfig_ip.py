import argparse
import copy

from fem.api.config import FemConfig
from fem.client import FemClient, FemClientError


class FemReconfigIp:

    def __init__(self):

        def_femip   = '192.168.2.2'
        def_femport = 6969

        parser = argparse.ArgumentParser(description='FemReconfigIp.py - reconfigure FEM IP settings',
                                         formatter_class=argparse.ArgumentDefaultsHelpFormatter)

        parser.add_argument("--femip",   help="Set existing FEM IP",   type=str, default=def_femip)
        parser.add_argument("--femport", help="Set existing FEM port", type=int, default=def_femport)
        parser.add_argument("--newip",   help="Set new FEM IP",        type=str)
        parser.add_argument("--newmask", help="Set new IP mask",       type=str)
        parser.add_argument("--newgw",   help="Set new gateway addr",  type=str)

        self.args = parser.parse_args()

    def run(self):

        # Sanity check that at least one of new IP, mask or gateway is specified
        if self.args.newip is None and self.args.newmask is None and self.args.newgw is None:
            print("ERROR: you must specify at least one of new IP address, mask or gateway")
            return

        # Open a connection to the FEM
        try:
            print(f"Connecting to FEM at IP address {self.args.femip} port {self.args.femport} ... ", end="")
            self.fem = FemClient((self.args.femip, self.args.femport))
            print("OK")
        except FemClientError as e:
            print("failed to connect", str(e))
            return

        # Read the FEM configuration EEPROM
        try:
            print("Reading FEM EEPROM configuration ... ", end="")
            fem_config = self.fem.configRead()
            print("OK")

        except FemClientError as e:
            print("failed:", str(e))
            self.fem.close()
            return

        # Check that the FEM has a correctly initialised EEPROM config
        if fem_config.magicWord != FemConfig.CONFIG_MAGIC_WORD:
            print("ERROR: FEM does not have a correctly configured EEPROM, not changing IP configuration. Please seek expert assistance.")
            self.fem.close()
            return
        else:
            print(f"FEM has correctly initialised EEPROM configuration with existing IP: {fem_config.net_ip_addr_str()} mask: {fem_config.net_ip_mask_str()} gateway: {fem_config.net_ip_gw_str()}")

        # Update the configuration with the new parameters that have been specified
        updated_config_ok = True
        new_fem_config = copy.deepcopy(fem_config)

        if self.args.newip is not None:
            newip = self.split_addr(self.args.newip, "IP address")
            if newip is not None:
                new_fem_config.net_ip = newip
            else:
                updated_config_ok = False

        if self.args.newmask is not None:
            newmask = self.split_addr(self.args.newmask, "mask")
            if newmask is not None:
                new_fem_config.net_mask = newmask
            else:
                updated_config_ok = False

        if self.args.newgw is not None:
            newgw = self.split_addr(self.args.newgw, "gateway")
            if newgw is not None:
                new_fem_config.net_gw = newgw
            else:
                updated_config_ok = False

        if updated_config_ok:

            config_updated = False
            if new_fem_config.net_ip != fem_config.net_ip or new_fem_config.net_mask != fem_config.net_mask or new_fem_config.net_gw != fem_config.net_gw:

                print(f"\nReady to write FEM EEPROM configuration with updated IP: {new_fem_config.net_ip_addr_str()} mask: {new_fem_config.net_ip_mask_str()} gateway: {new_fem_config.net_ip_gw_str()}")

                reply = input("\n      Are you SURE you want to proceed? (y/N) : ")

                if reply.lower() == "y" or reply.lower() == "yes":

                    print("\nWriting EEPROM configuration to FEM ... ", end="")
                    try:
                        self.fem.configWrite(new_fem_config)
                        print("done")
                        config_updated = True
                    except FemClientError as e:
                        # Some FEM code versions report write transaction failed at this point, so check and ignore
                        if str(e) == "FEM write transaction failed: ":
                            print("done")
                            config_updated = True
                        else:
                            print(f"FAILED: {e}")

                    # If the configuration was updated OK, read it back and validate
                    if config_updated:

                        print("Reading back FEM configuration to verify ... ", end="")
                        try:
                            updated_fem_config = self.fem.configRead()
                        except FemClientError as e:
                            print(f"FAILED: {e}")
                        else:
                            if updated_fem_config.net_ip == new_fem_config.net_ip and  \
                               updated_fem_config.net_mask == new_fem_config.net_mask and \
                               updated_fem_config.net_gw == new_fem_config.net_gw:
                                print("OK, configuration verified, new network settings will become active at next FEM reboot")
                            else:
                                print("ERROR: mismatch in verified FEM configuraiton, please seek expert assistance")

                else:
                    print("OK, not changing FEM EEPROM configuration")

            else:
                print("No IP settings will change - not updating FEM configuration")
        else:
            print("Not updating configuration due to parameter error")

        # Close the FEM connection
        self.fem.close()

    def split_addr(self, addr, name):

        try:
            values = addr.split('.')
        except ValueError:
            print(f"Specified {name} {addr} has incorrect format")
            return None

        if len(values) != 4:
            print(f"Specified {name} {addr} has wrong number of octets")
            return None

        try:
            addr_octets = [int(octet) for octet in values]
        except ValueError:
            print(f"Specified {name} {addr} has illegal octet value")
            return None

        return addr_octets

def main():

    fri = FemReconfigIp()
    fri.run()

if __name__ == '__main__':

    main()
