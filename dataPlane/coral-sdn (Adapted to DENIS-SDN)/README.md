# CORAL-SDN Infrastructure plane protocol adapted to work with DENIS-SDN Controller


**coral_br.c** for Border Router
 motes \
**coral_node.c** for normal motes

The files should be placed in \contiki\core\net\coral-sdn folder.

To use the protocol in normal nodes include: 

#include "net/coral-sdn/coral.h"

#include "net/coral-sdn/coral_node.c"

To use the protocol in border router nodes include: 
#include "net/coral-sdn/coral.h"
#include "net/coral-sdn/coral_br.c"
