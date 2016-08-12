from pybakalib.modules.messages import ReceivedMessages
from pybakalib.modules.notice_board import NoticeBoard
from pybakalib.modules.profile import Profile
from pybakalib.modules.weights import parse_weights
from pybakalib.modules.marks import MarksModule

MODULES = {
    'znamky': MarksModule,
    'predvidac': parse_weights,
    'login': Profile,
    'nastenka': NoticeBoard,
    'prijate': ReceivedMessages
}