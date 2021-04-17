#!/bin/bash

if  [ $# -lt 1 ];then
    echo "Please Input A Argument"
    exit 1
fi

if [ -z $CURRENT_DIR ]; then
    CURRENT_DIR=`pwd`
fi


AGENT_PID=$CURRENT_DIR/agent.pid




# 启动agent
case $1 in

start)
    python3  $CURRENT_DIR/manager.py start ;;

stop)
    python3  $CURRENT_DIR/manager.py stop ;;

restart)
    python3  $CURRENT_DIR/manager.py stop
    sleep 2
    python3  $CURRENT_DIR/manager.py start ;;

status)
    if [ -f $AGENT_PID ]; then
      echo "Agent Is Running......"
    else
      echo "Agent Is Not Running......"
    fi
    ;;

*)
    echo "Usage: bash control.sh {start|stop|restart|status}"
    exit 1 ;;

esac