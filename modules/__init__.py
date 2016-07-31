from modules.profile import Profile
from modules.weights import parse_weights
from modules.marks import MarksModule

MODULES = {
    'znamky': MarksModule,
    'predvidac': parse_weights,
    'login': Profile
}