from agno.playground import Playground

from agents.finance_agent import get_finance_agent


######################################################
## Routes for the Playground Interface
######################################################

# Get Agents to serve in the playground
finance_agent = get_finance_agent(debug_mode=True)

# Create a playground instance
playground = Playground(agents=[finance_agent])

# Get the router for the playground
playground_router = playground.get_async_router()
