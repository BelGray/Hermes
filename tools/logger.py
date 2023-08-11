# -*- coding: utf-8 -*-
from tools.BGConsole import BGC

class Log:
    @staticmethod
    def s(tag: str, body: str):
        BGC.write(f"[{tag}]    {body}", param=BGC.Param.BOLD, color=BGC.Color.GREEN)

    @staticmethod
    def e(tag: str, body: str):
        BGC.write(f"[{tag}]    {body}", param=BGC.Param.BOLD, color=BGC.Color.RED)

    @staticmethod
    def w(tag: str, body: str):
        BGC.write(f"[{tag}]    {body}", param=BGC.Param.BOLD, color=BGC.Color.MUSTARD)

    @staticmethod
    def i(tag: str, body: str):
        BGC.write(f"[{tag}]    {body}", param=BGC.Param.BOLD, color=BGC.Color.BLUE)

    @staticmethod
    def sql(tag: str, body: str, table_name: str):
        BGC.write(f"[{tag}][{table_name}]    {body}", param=BGC.Param.BOLD, color=BGC.Color.CYAN)
