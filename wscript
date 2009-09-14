#! /usr/bin/env python
# encoding: utf-8
# Jaap Haitsma, 2008

# the following two variables are used by the target "waf dist"
VERSION='0.0.1'
APPNAME='plugster'

# these variables are mandatory ('/' are converted automatically)
srcdir = '.'
blddir = 'build'

def set_options(opt):
    opt.tool_options('compiler_cc')

def configure(conf):
    conf.check_tool('compiler_cc cc vala')
    conf.check_cfg(package='glib-2.0', uselib_store='GLIB', atleast_version='2.10.0', mandatory=1, args='--cflags --libs')
    conf.check_cfg(package='gtk+-2.0', uselib_store='GTK', atleast_version='2.10.0', mandatory=1, args='--cflags --libs')
    conf.check_cfg(package='gstreamer-0.10', uselib_store='GSTREAMER', atleast_version='0.10.0', mandatory=1, args='--cflags --libs')
    conf.check_cfg(package='goocanvas', uselib_store='GOOCANVAS', atleast_version='0.13', mandatory=1, args='--cflags --libs')
    conf.check_cfg(package='pango', uselib_store='PANGO', atleast_version='0.22', mandatory=1, args='--cflags --libs')
    conf.check_cfg(package='libxml-2.0', uselib_store='XML', atleast_version='2.6.32', mandatory=1, args='--cflags --libs')

def build(bld):
    bld.add_subdirs('src')
    bld.install_files('${PREFIX}/share/plugster/ui', 'src/ui/mainwindow.ui')

def shutdown():
    pass
