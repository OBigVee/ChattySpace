from brownie import Chat, accounts, network


def main():
    # requires brownie account to have been created
    if network.show_active()=='development':
        # add these accounts to metamask by importing private key
        owner = accounts[0]
        Chat.deploy({'from':accounts[0]})

    elif network.show_active() == '<input network>':
        # add these accounts to metamask by importing private key
        owner = accounts.load("<account name>")
        Chat.deploy({'from':owner})