# Imports ######################################################################


# Globals ######################################################################


# Library ######################################################################
# exceptions ###############################################################
class PortAssignError(Exception):
    """
    Raised when assigning a UART port fails.
    """
    pass
class CreateUartError(Exception):
    """
    Raised when initializing the uart for communication fails.
    """
    pass
class DestroyUartError(Exception):
    """
    Raised when stopping the uart communication channel fails.
    """
    pass

# Main #########################################################################
def main():
    pass

if __name__ == '__main__':
    main()
