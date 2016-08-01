from modules.messages import ReceivedMessages
from modules.notice_board import NoticeBoard
from modules.profile import Profile
from modules.weights import parse_weights
from modules.marks import MarksModule

MODULES = {
    'znamky': MarksModule,
    'predvidac': parse_weights,
    'login': Profile,
    'nastenka': NoticeBoard,
    'prijate': ReceivedMessages
}