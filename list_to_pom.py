# Similar:
# https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwj_p9qa4qb-AhUig_0HHZnrAUgQFnoECAMQAQ&url=https%3A%2F%2Fgist.github.com%2Febd2b69dc4078065a837e9183f48a873&usg=AOvVaw0Mb6PgGasWXC_rJs8Yz7vd
# https://www.google.com/url?sa=t&rct=j&q=&esrc=s&source=web&cd=&cad=rja&uact=8&ved=2ahUKEwj_p9qa4qb-AhUig_0HHZnrAUgQFnoECAUQAQ&url=https%3A%2F%2Fgist.github.com%2Fxshyamx%2F5927550&usg=AOvVaw1cTEExnNCzpdGh1RCXeuex

import sys
import aiohttp
import asyncio
import textwrap

filename = sys.argv[1]

def items():
    with open(filename) as f:
        for line in f.readlines():
            # Cut .jar
            line = line[:-5]
            split = line.split('-')
            name = '-'.join(split[:-1])
            version = split[-1]
            if not name:
                continue
            yield name, version

# Semaphore to prevent rate limiting kicking in
semaphore = asyncio.Semaphore(5)
async def get_package_pom_entry(session, name, version, not_found):
    async with semaphore:
        async with session.get(f"https://search.maven.org/solrsearch/select?q=a:{name}+AND+v:{version}&rows=1&wt=json") as resp:
            resp = await resp.json()
        docs = resp['response']['docs']
        if not docs:
            not_found.append(name)
            return
        item = docs[0]
        return f"""<dependency>
    <groupId>{item['g']}</groupId>
    <artifactId>{item['a']}</artifactId>
    <version>{version}</version>
</dependency>"""


pom = """\
<project>
	<modelVersion>4.0.0</modelVersion>

	<groupId>test</groupId>
	<artifactId>test</artifactId>
	<version>1</version>

	<dependencies>
{dependencies}
	</dependencies>
</project>"""


async def main():
    not_found = []
    async with aiohttp.ClientSession() as session:
        requests = [get_package_pom_entry(session, name, version, not_found) for name,version in items()]
        ret = await asyncio.gather(*requests)
    ret = [x for x in ret if x]
    dependencies = textwrap.indent('\n'.join(ret), 12*' ')
    with open('pom.xml', 'w+') as f:
        f.write(pom.format(dependencies=dependencies))
    print("Not found: ")
    for x in not_found:
        print(x)

asyncio.run(main())
