from StateRedis import StateRedis
from events import *
from sourcecontrol import *
from shell import *
from publishers import *

WORKDIR=os.path.expanduser("/mnt/cicada/workspace")
PUBDIR=os.path.expanduser("/mnt/cicada/artifacts")
QUEUE_EVENT = StateRedis()

LISTEN = [
    TestOnEvent('libinjection'),
    TestOnTime(minute='0', hour='23')
]

POLLERS = {
    'statsite': {
        'listen': [
            TestOnTime(minute='10', hour='3'),
        ],
        'exec': PollGit(
            'statsite',
            'https://github.com/armon/statsite.git',
            QUEUE_EVENT
        )
    },
    'protobuf-c': {
        'listen': [
            TestOnTime(minute='10', hour='2'),
        ],
        'exec': PollGit('protobuf-c',
                        'https://github.com/protobuf-c/protobuf-c', QUEUE_EVENT)
    },
    'poll-git-openssl': {
        'listen': [
            TestOnTime(minute='10', hour='1'),
        ],
        'exec': PollGit('openssl',
                        'git://git.openssl.org/openssl.git', QUEUE_EVENT)
    },
    'poll-git-mruby': {
        'listen': [
            TestOnTime(minute='20', hour='1'),
        ],
        'exec': PollGit('mruby',
                        'https://github.com/mruby/mruby.git', QUEUE_EVENT)
    },
    'poll-svn-stringencoders': {
        'listen': [
            TestOnInterval(minutes=10),
        ],
        'exec': PollSVN('stringencoders',
                        'http://stringencoders.googlecode.com/svn/trunk/',
                        QUEUE_EVENT)
    }
}

LISTEN = [
    TestOnEvent('libinjection'),
    TestOnTime(minute='0', hour='23'),
]

MRUBY = {
   'build-gcc': {
        'listen': [ TestOnEvent('mruby') ],
        'source': CheckoutGit('https://github.com/mruby/mruby.git', 'mruby'),
        'exec': ExecuteShell("""
cd mruby
make
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
   'build-clang': {
        'listen': [ TestOnEvent('mruby') ],
        'source': CheckoutGit('https://github.com/mruby/mruby.git', 'mruby'),
        'exec': ExecuteShell("""
cd mruby
CC=clang make -e
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'cppcheck': {
        'listen': [ TestOnEvent('mruby') ],
        'source': CheckoutGit('https://github.com/mruby/mruby.git', 'mruby'),
        'exec': ExecuteShell("""
cppcheck --version
cd mruby
cppcheck --quiet --error-exitcode=2 --enable=all --inconclusive \
    --suppress=variableScope  \
    --std=c89 --std=posix \
    --template '{file}:{line} {severity} {id} {message}' src
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'clang-static-analyzer': {
        'listen': [ TestOnEvent('mruby') ],
        'source': CheckoutGit('https://github.com/mruby/mruby.git', 'mruby'),
        'exec': ExecuteShell("""
cd mruby
scan-build -o /mnt/cicada/workspace/mruby/clang-static-analyzer/ --status-bugs make -e
cd /mnt/cicada/workspace/mruby/clang-static-analyzer/
# scan-build generates a date-based file, starting with year.  move to fixed directory
rm -rf csa
mv 20* csa
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('csa', PUBDIR, 'csa/index.html', 'analysis')
        ]
    },
    'stack': {
        'listen': [ TestOnEvent('stack') ],
        'source': CheckoutGit('https://github.com/mruby/mruby.git', 'mruby'),
        'exec': ExecuteShell("""
export LD_LIBRARY_PATH=/usr/local/lib
export PATH=/mnt/stack/build/bin/:$PATH
cd mruby
find . -name '*.ll' -o -name '*.ll.out' | xargs rm -f
stack-build make
poptck
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('protobuf-c/pstack.txt', PUBDIR, 'pstack.txt', 'analysis'),
        ]
    }    
}

STATSITE = {
   'build-gcc': {
        'listen': [ TestOnEvent('statsite') ],
        'source': CheckoutGit('https://github.com/armon/statsite.git', 'statsite'),
        'exec': ExecuteShell("""
cd statsite
make
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
   'build-clang': {
        'listen': [ TestOnEvent('statsite') ],
        'source': CheckoutGit('https://github.com/armon/statsite.git', 'statsite'),
        'exec': ExecuteShell("""
cd statsite
CC=clang make -e
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'cppcheck': {
        'listen': [ TestOnEvent('statsite') ],
        'source': CheckoutGit('https://github.com/armon/statsite.git', 'statsite'),
        'exec': ExecuteShell("""
cppcheck --version
cd statsite
cppcheck --quiet --error-exitcode=2 --enable=all --inconclusive \
    --suppress=variableScope  \
    --std=c89 --std=posix \
    --template '{file}:{line} {severity} {id} {message}' src
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'clang-static-analyzer': {
        'listen': [ TestOnEvent('statsite') ],
        'source': CheckoutGit('https://github.com/armon/statsite.git', 'statsite'),
        'exec': ExecuteShell("""
cd statsite
scons -c
scan-build -o /mnt/cicada/workspace/openssl/clang-static-analyzer/ --status-bugs make -e
cd /mnt/cicada/workspace/statsite/clang-static-analyzer/
# scan-build generates a date-based file, starting with year.  move to fixed directory
rm -rf csa
mv 20* csa
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('csa', PUBDIR, 'csa/index.html', 'analysis')
        ]
    },
    'stack': {
        'listen': [ TestOnEvent('stack') ],
        'source': CheckoutGit('https://github.com/armon/statsite.git', 'statsite'),
        'exec': ExecuteShell("""
export LD_LIBRARY_PATH=/usr/local/lib
export PATH=/mnt/stack/build/bin/:$PATH
cd statsite
scons -c
find . -name '*.ll' -o -name '*.ll.out' | xargs rm -f
stack-build make
poptck
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('protobuf-c/pstack.txt', PUBDIR, 'pstack.txt', 'analysis'),
        ]
    }
}

PROTOBUFC = {
    'build-test-gcc': {
        'listen': [ TestOnEvent('protobuf-c') ],
        'source': CheckoutGit('https://github.com/protobuf-c/protobuf-c.git', 'protobuf-c'),
        'exec': ExecuteShell("""
export LD_LIBRARY_PATH=/usr/local/lib
cd protobuf-c
./autogen.sh
CFLAGS=-I/usr/local/include LDFLAGS=-L/usr/local/lib ./configure
export CFLAGS='-I/usr/local/include -Wall -Wextra -Werror'
make -e
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'build-test-clang': {
        'listen': [ TestOnEvent('protobuf-c') ],
        'source': CheckoutGit('https://github.com/protobuf-c/protobuf-c.git', 'protobuf-c'),
        'exec': ExecuteShell("""
export LD_LIBRARY_PATH=/usr/local/lib
cd protobuf-c
./autogen.sh
CC=clang CXX='clang++' CFLAGS=-I/usr/local/include LDFLAGS=-L/usr/local/lib ./configure
export CFLAGS="-I/usr/local/include -Weverything -Wno-cast-align -Wno-documentation -Wno-format-nonliteral"
make -e
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'cppcheck': {
        'listen': [ TestOnEvent('protobuf-c') ],
        'source': CheckoutGit('https://github.com/protobuf-c/protobuf-c.git', 'protobuf-c'),
        'exec': ExecuteShell("""
export LD_LIBRARY_PATH=/usr/local/lib
cppcheck --version
cd protobuf-c
./autogen.sh
cppcheck --quiet --error-exitcode=2 --enable=all --inconclusive \
    --suppress=unusedFunction \
    --std=c89 --std=posix \
    --template '{file}:{line} {severity} {id} {message}' protobuf-c
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'clang-static-analyzer': {
        'listen': [ TestOnEvent('protobuf-c') ],
        'source': CheckoutGit('https://github.com/protobuf-c/protobuf-c.git', 'protobuf-c'),
        'exec': ExecuteShell("""
export LD_LIBRARY_PATH=/usr/local/lib
cd protobuf-c
./autogen.sh
./configure
make clean
CFLAGS=-I/usr/local/include LDFLAGS=-L/usr/local/lib ./configure
scan-build -o /mnt/cicada/workspace/openssl/clang-static-analyzer/ --status-bugs make
cd /mnt/cicada/workspace/openssl/clang-static-analyzer/
# scan-build generates a date-based file, starting with year.  move to fixed directory
rm -rf csa
mv 20* csa
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('csa', PUBDIR, 'csa/index.html', 'analysis')
        ]
    },
    'stack': {
        'listen': [ TestOnEvent('stack') ],
        'source': CheckoutGit('https://github.com/protobuf-c/protobuf-c.git', 'protobuf-c'),
        'exec': ExecuteShell("""
export LD_LIBRARY_PATH=/usr/local/lib
export PATH=/mnt/stack/build/bin/:$PATH
cd protobuf-c
./autogen.sh
stack-build ./configure
stack-build make clean
find . -name '*.ll' -o -name '*.ll.out' | xargs rm -f
stack-build make
poptck
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('protobuf-c/pstack.txt', PUBDIR, 'pstack.txt', 'analysis'),
        ]
    }

}

OPENSSL = {
    'build-test': {
        'listen': [ TestOnEvent('openssl') ],
        'source': CheckoutGit('git://git.openssl.org/openssl.git', 'openssl'),
        'exec': ExecuteShell("""
cd openssl
./config
make
make check
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'coverage': {
        'listen': [ TestOnEvent('openssl') ],
        'source': CheckoutGit('git://git.openssl.org/openssl.git', 'openssl'),
        'exec': ExecuteShell("""
cd openssl
./config -O0 -fprofile-arcs -ftest-coverage
make
lcov -b . -d . --zerocounters
make test
lcov -c -d . --path /mnt/cicada/workspace/openssl/build-test/openssl -o openssl.info
lcov -d . --remove openssl.info '/usr/include*' -o openssl.info
# lcov -d . --remove openssl.info '*/test/*' -o openssl.info
# lcov -d . --remove openssl.info '*/engines/*' -o openssl.info
genhtml --branch-coverage -o ../lcov-html openssl.info
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('lcov-html', PUBDIR, '/lcov-html/index.html', 'coverage')
        ]
    },
    'cppcheck': {
        'listen': [ TestOnEvent('openssl') ],
        'source': CheckoutGit('git://git.openssl.org/openssl.git', 'openssl'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ],
        'exec': ExecuteShell("""
cppcheck --version
cd openssl
cppcheck --quiet --error-exitcode=2 --enable=all --inconclusive \
    --suppress=variableScope  \
    --std=c89 --std=posix \
    --template '{file}:{line} {severity} {id} {message}' .
""")
    },
    'clang-static-analyzer': {
        'listen': [ TestOnEvent('openssl') ],
        'source': CheckoutGit('git://git.openssl.org/openssl.git', 'openssl'),
        'exec': ExecuteShell("""
cd openssl
./config
make clean
./config
scan-build -o /mnt/cicada/workspace/openssl/clang-static-analyzer/ --status-bugs make
cd /mnt/cicada/workspace/openssl/clang-static-analyzer/
# scan-build generates a date-based file, starting with year.  move to fixed directory
rm -rf csa
mv 20* csa
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('csa', PUBDIR, 'csa/index.html', 'analysis')
        ]
    },
    'stack': {
        'listen': [ TestOnEvent('stack') ],
        'source': CheckoutGit('git://git.openssl.org/openssl.git', 'openssl'),
        'exec': ExecuteShell("""
export PATH=/mnt/stack/build/bin/:$PATH
cd openssl
stack-build ./config
stack-build make clean
find . -name '*.ll' -o -name '*.ll.out' | xargs rm -f
stack-build make
poptck
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('openssl/pstack.txt', PUBDIR, 'pstack.txt', 'analysis'),
        ]
    }
}

STRINGENCODERS = {
    'build-test-gcc': {
        'listen': [ TestOnEvent('stringencoders') ],
        'source': CheckoutSVN('http://stringencoders.googlecode.com/svn/trunk/', 'stringencoders'),
        'exec': ExecuteShell('cd stringencoders && ./bootstrap.sh && ./configure && make && make test'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'build-test-clang': {
        'listen': [ TestOnEvent('stringencoders') ],
        'source': CheckoutSVN('http://stringencoders.googlecode.com/svn/trunk/', 'stringencoders'),
        'exec': ExecuteShell("""
cd stringencoders
./bootstrap.sh
# we set cc=clang for configure
# but set the very strict cflags for make only... autoconf emits bad c test and
#  breaks
CC=clang CXX='clang++' ./configure
export CFLAGS="-Isrc -Weverything -Wno-cast-align -Wno-documentation -Wno-format-nonliteral"
make -e && make -e test
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'cppcheck': {
        'listen': [ TestOnEvent('stringencoders') ],
        'source': CheckoutSVN('http://stringencoders.googlecode.com/svn/trunk/', 'stringencoders'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ],
        'exec': ExecuteShell("""
cppcheck --version
cd stringencoders
cppcheck --quiet --error-exitcode=2 --enable=all --inconclusive \
    --suppress=variableScope  \
    --std=c89 --std=posix \
    --template '{file}:{line} {severity} {id} {message}' \
    -DINFINITY -DNAN \
    src test
""")
    },
    'clang-static-analyzer': {
        'listen': [ TestOnEvent('stringencoders') ],
        'source': CheckoutSVN('http://stringencoders.googlecode.com/svn/trunk/', 'stringencoders'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('csa', PUBDIR, 'csa/index.html', 'analysis')
        ],
        'exec':  ExecuteShell("""
clang --version
cd stringencoders
./bootstrap.sh && ./configure
make clean
scan-build -o /mnt/cicada/workspace/stringencoders/clang-static-analyzer/ --status-bugs make
ERR=$?
cd /mnt/cicada/workspace/stringencoders/clang-static-analyzer/
rm -rf csa
mv 20* csa
exit ${ERR}
""")
    },
    'codecoverage': {
        'listen': [ TestOnEvent('stringencoders') ],
        'source': CheckoutSVN('http://stringencoders.googlecode.com/svn/trunk/', 'stringencoders'),
        'exec': ExecuteShell('cd stringencoders && ./bootstrap.sh && ./configure --enable-gcov && make clean && make lcov-html'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('stringencoders/lcov-html/html', PUBDIR, 'html/stringencoders/src/index.html', 'coverage')
        ]
    },
    'valgrind': {
        'listen': [ TestOnEvent('stringencoders') ],
        'source': CheckoutSVN('http://stringencoders.googlecode.com/svn/trunk/', 'stringencoders'),
        'exec': ExecuteShell('cd stringencoders && ./bootstrap.sh && ./configure && make clean && make valgrind'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console')
        ]
    },
    'stack': {
        'listen': [  TestOnEvent('stack') ],
        'source': CheckoutSVN('http://stringencoders.googlecode.com/svn/trunk/', 'stringencoders'),
        'exec'  : ExecuteShell("""#!/bin/bash
export PATH=/mnt/stack/build/bin/:$PATH
cd stringencoders
./bootstrap.sh
stack-build ./configure
stack-build make clean
stack-build make
poptck
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('stringencoders/pstack.txt', PUBDIR, 'pstack.txt', 'analysis'),
        ]
    }
}

LIBINJECTION = {
    'libinjection-build-test': {
        'listen'  : LISTEN,
        'source'  : CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'    : ExecuteShell('gcc --version && cd libinjection && ./autogen.sh && ./configure && make clean && make check'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('libinjection/src/test-suite.log', PUBDIR,
                            'test-suite.txt', 'test log')
        ]
    },
    'libinjection-build-test-g++': {
        'listen'  : LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec': ExecuteShell('g++ --version && cd libinjection && ./autogen.sh && ./configure && make clean && CC=g++ make check'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('libinjection/src/test-suite.log', PUBDIR,
                            'test-suite.txt', 'test log')
        ]
    },
    'libinjection-build-test-clang': {
        'listen'  : LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec': ExecuteShell("""
clang --version
cd libinjection
./autogen.sh
./configure
make clean
CC=clang CFLAGS="-g -O3 -Weverything -Wno-padded -Wno-covered-switch-default -Werror" make -e test
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('libinjection/src/test-suite.log', PUBDIR,
                            'test-suite.txt', 'test log')
        ]
    },
    'libinjection-cppcheck': {
        'listen' : LISTEN,
        'source' : CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'   : ExecuteShell('cppcheck --version && cd libinjection && ./autogen.sh && ./configure && make cppcheck'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-clang-static-analyzer': {
        'listen' : LISTEN,
        'source' : CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'   : ExecuteShell('clang --version && cd libinjection && ./autogen.sh && ./clang-static-analyzer.sh'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-loc': {
        'listen' : LISTEN,
        'source' : CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'   : ExecuteShell('cd libinjection/src && cloc libinjection*.h libinjection*.c'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-pyflakes': {
        'listen': LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec': ExecuteShell('cd libinjection/src && pyflakes *.py'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-pylint': {
        'listen': LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        # disable 'too-many-lines' warning
        'exec': ExecuteShell('/usr/local/bin/pylint --disable=C0302 --msg-template="{path}:{line}: [{msg_id}({symbol}), {obj}]" libinjection/src/*.py'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-python-build-test': {
        'listen': LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec': ExecuteShell('cd libinjection && make clean && cd python && make check'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-php-build-test': {
        'listen': LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec': ExecuteShell('cd libinjection && make clean && cd php && make test'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-lua-build-test': {
        'listen': LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec': ExecuteShell('cd libinjection && make clean && cd lua && make test'),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-samples-positive': {
        'listen': LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'   : ExecuteShell("""
cd libinjection
./autogen.sh
./configure
make clean
cd src
make reader
./reader -t -i -m 21 ../data/sqli-*.txt
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-samples-negative': {
        'listen': LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'   : ExecuteShell("""
cd libinjection
./autogen.sh
./configure
make clean
cd src
make reader
./reader -t -m 22 ../data/false_positives.txt
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-coverage-unittest': {
        'listen'  : LISTEN,
        'source'  : CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'    : ExecuteShell("cd libinjection && ./autogen.sh && ./configure && make clean && make coverage-testdriver"),
        'publish' : [
            # 1. file relative to workspace  for PublishConsole, it's empty
            # 2. link url
            # 2. linktext
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('libinjection/src/lcov-html', PUBDIR, '/lcov-html/libinjection/src/index.html', 'coverage')
        ]
    },
    'libinjection-coverage-data': {
        'listen'  : LISTEN,
        'source'  : CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'    : ExecuteShell("cd libinjection && ./autogen.sh && ./configure && make clean && make coverage-reader"),
        'publish' : [
            # 1. file relative to workspace  for PublishConsole, it's empty
            # 2. link url
            # 2. linktext
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('libinjection/src/lcov-html', PUBDIR, '/lcov-html/libinjection/src/index.html', 'coverage')
        ]
    },
    'libinjection-speed': {
        'listen'  : LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec' : ExecuteShell("cd libinjection && ./autogen.sh && ./configure && make test_speed"),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-valgrind': {
        'listen'  : LISTEN,
        'source': CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec' : ExecuteShell("cd libinjection && ./autogen.sh && ./configure && make clean && nice make valgrind"),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'libinjection-gprof': {
        'listen'  : LISTEN,
        'source'  : CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'    : ExecuteShell("""#!/bin/bash
cd libinjection
./autogen.sh
./configure
make clean
cd src
make reader-gprof
./reader-gprof -s -q ../data/sqli-*.txt ../data/false-*.txt
gprof ./reader-gprof gmon.out
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
        ]
    },
    'stack': {
        'listen'  : [ TestOnEvent('stack'), ],
        'source'  : CheckoutGit('https://github.com/client9/libinjection.git', 'libinjection'),
        'exec'    : ExecuteShell("""#!/bin/bash
export PATH=/mnt/stack/build/bin/:$PATH
cd libinjection
./configure
stack-build make clean
stack-build make allbin
poptck
"""),
        'publish': [
            PublishArtifact('console.txt', PUBDIR, 'console.txt', 'console'),
            PublishArtifact('libinjection/pstack.txt', PUBDIR, 'pstack.txt', 'analysis'),
        ]
    }
}

PROJECTS = {
    'pollers': POLLERS
    , 'libinjection': LIBINJECTION
    , 'stringencoders': STRINGENCODERS
    , 'openssl': OPENSSL
    , 'statsite': STATSITE
    , 'protobuf-c': PROTOBUFC
    , 'mruby': MRUBY
}
