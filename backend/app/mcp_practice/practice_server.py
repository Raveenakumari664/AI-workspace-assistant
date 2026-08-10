from mcp.server.fastmcp import FastMCP
mcp= FastMCP("calculator server")

@mcp.tool()
def add_numbers(a: int, b: int)-> int:
    "add two numbers"
    return a+b

@mcp.tool()
def greet(name: str)-> str:
    "greeting"
    return f"hello, {name}! welcome to MCP"

if __name__ =="__main__":
    mcp.run()
