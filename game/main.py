from fastapi import FastAPI, Request
import uvicorn

from __init__ import *
from graphQL.handle import *

app = FastAPI()

@app.get(conf["url_prefix"]+"/")
async def index():
    return {"No u": ""}

@app.post(conf["url_prefix"]+"/graphql")
async def handle(request: Request):
    data = await request.json()
    print(data) # DEBUG
    if request.headers.get("user-agent") != "dynamite/59 CFNetwork/1333.0.4 Darwin/21.5.0":
        return graphql_like_error(error_dic["not_from_game_connection"])
    
    schema = strawberry.Schema(query = Query, mutation = Mutation, config = StrawberryConfig(auto_camel_case = False))
    if "variables" not in data.keys():
        graphql_ret = await schema.execute(data['query'], context_value=request.headers.get("x-soudayo"))
    else:
        graphql_ret = await schema.execute(data['query'], data['variables'], request.headers.get("x-soudayo"))
    print(graphql_ret)  # DEBUG

    if graphql_ret.errors != None:
        err_msg = ""
        for err in graphql_ret.errors:
            err_msg += err.message + " "
        return graphql_like_error(err_msg)

    print("\n\n",graphql_ret.__dict__)
    return graphql_ret.__dict__


if __name__ == "__main__":
    os.chdir(sys.path[0])
    if conf["https"]:
        uvicorn.run("main:app",
            host = "0.0.0.0", 
            port = conf["api_port"], 
            reload = conf["server_hot_reload"],
            ssl_keyfile = conf["https_key"], 
            ssl_certfile = conf["https_cert"]
        )
    else:
        uvicorn.run("main:app",
            host = "0.0.0.0", 
            port = conf["api_port"], 
            reload = conf["server_hot_reload"]
        )