import aiohttp
from aiohttp import web
import asyncio
from urllib.parse import urljoin, urlparse, urlunparse

#cache_time = 10 # Time for which a "healthy" result will be cached
hosts = ['http://127.0.0.1:5001', 'http://127.0.0.1:5002']

node_index = 0

async def handle(request):
  """Take a request and proxy it via an eligible node """ 

  print('--')
  print(f'Received request {request!r}')
  print(f'{request.method} {request.rel_url} HTTP {request.version.major}.{request.version.minor}')
  nodes = await get_eligible_nodes()
  if nodes:
    path = request.path
    url = urljoin(nodes[node_index], path) 
    print(f'URL: {url}')
  else:
    raise aiohttp.web.HTTPBadGateway('No eligible nodes')
  async with aiohttp.ClientSession() as session:
    async with session.get(url, params=request.query) as resp:
      text = await resp.text()
      return web.Response(text=text) 

async def check_node(url):
  """Check a given URL to see if it is eligible to receive traffic

  Parameters:
  url (string): URL to check

  This will perform a health check on the given URL. Returns the supplied
  URL if the health check succeeds. Returns None if the health check fails.
  """

  async with aiohttp.ClientSession() as session:
    try:
      async with session.get(urljoin(url, 'healthcheck')) as response:
        status = response.status
        if status >= 200 and status < 300:
          return url
    except Exception as e:
      print(f'Unable to connect to {url}: {e}')


async def get_eligible_nodes():
  """Return a list of nodes eligible to receive traffic

  This function will run a health check on every node in the load balancer and will 
  return a tuple containing the URLs for all nodes for which the health check was 
  successful 
  """

  tasks = [check_node(h) for h in hosts]
  good_hosts = filter(lambda h: h != None, await asyncio.gather(*tasks))
  return tuple(good_hosts)

app = web.Application()
app.add_routes([web.route('*', '/{tail:.*}', handle)])

if __name__ == '__main__':
  web.run_app(app)