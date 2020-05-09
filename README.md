# mrp_subcontracting-backport
backport of mrp_subcontracting* modules from Odoo CE 13.0 to Odoo 12.0

breaking news! The day I annonced the port, Pedro Baeza told me on Twitter they also did the backport on their side, taking care about adapting the tests in their case. We will probably compare the 2 codebases now...
https://github.com/Tecnativa/manufacture/tree/12.0-add-mrp_subcontracting/mrp_subcontracting

It works for us in all the use cases demoed by Odoo SA for v13.
Here is a basic demo: https://youtu.be/K9IYBeBwm2E

However we didn't make the tests pass. The reason is v13 tests are highly dependent on v13 demo data from lower lever modules that are quite different
from v12 demo data and we couldn't afford the time to update them all.

If you feel you can make these tests pass and eventually put this module at the OCA feel free to tell us.
Putting this module at the OCA would be temporary because it's in the core in v13 and coming v14. It's also
questionnable if the code should be all re-formated according to PEP8 and OCA standards because it would make it harder
to backport eventual Odoo SA fixes and because of the temporary nature of this backport.


