namespace Plugster
{

class Application : Object
{
    private MainWindowController main_window;
    private static string prefix;

    public static void main(string[] args)
    {
        Gtk.init(ref args);
        Gst.init(ref args);
        prefix = GLib.Path.get_dirname(GLib.Path.get_dirname(args[0]));

        var app = new Application();
        GLib.Idle.add(app.start);

        Gtk.main();
    }

    public bool start()
    {
        main_window = new MainWindowController();
        main_window.initialize(prefix);
        return false;
    }
}

}

