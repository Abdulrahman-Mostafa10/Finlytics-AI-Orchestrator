from Mcp.goal_tools import *
from Mcp.spending_tracker_tools import *
from Mcp.personalization_tools import *
from Mcp.questionnaire_tools import *

if __name__ == "__main__":
    mcp.run(transport='streamable-http') # for fastapi testing
    # mcp.run(transport='stdio') # for claude testing