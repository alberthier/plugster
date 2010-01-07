using Gtk;
using Goo;

namespace Plugster
{

class MainWindowController : GLib.Object
{
    private Window mainwindow;
    private PipelineController pipeline_controller;
    private PropertyEditorController property_editor_controller;

    public void initialize(string prefix)
    {
        Builder builder = new Builder();
        try {
            if (builder.add_from_file(prefix + "/share/plugster/ui/mainwindow.ui") > 0) {
                mainwindow = (Window) builder.get_object("mainwindow");
                mainwindow.destroy += quit_app;

                var elements_treeview_scrollwindow = (ScrolledWindow) builder.get_object("elements_treeview_scrollwindow");
                var pipeline_canvas_scrollwindow = (ScrolledWindow) builder.get_object("pipeline_canvas_scrollwindow");
                var property_editor_scrollwindow = (ScrolledWindow) builder.get_object("property_editor_scrollwindow");

                elements_treeview_scrollwindow.add(new ElementFactoriesWidget());
                PipelineCanvas canvas = new PipelineCanvas();
                pipeline_canvas_scrollwindow.add(canvas);

                pipeline_controller = new PipelineController(mainwindow, canvas);
                property_editor_controller = new PropertyEditorController();
                property_editor_scrollwindow.add(property_editor_controller.tree_view);
                pipeline_controller.pipeline_changed += property_editor_controller.on_pipeline_changed;

                Action action = (Action) builder.get_object("action_new");
                action.activate += pipeline_controller.reset;

                action = (Action) builder.get_object("action_open");
                action.activate += pipeline_controller.open;

                action = (Action) builder.get_object("action_save");
                action.activate += pipeline_controller.save;

                action = (Action) builder.get_object("action_save_as");
                action.activate += pipeline_controller.save_as;

                action = (Action) builder.get_object("action_quit");
                action.activate += quit_app;

                action = (Action) builder.get_object("action_undo");
                action.activate += undo;

                action = (Action) builder.get_object("action_redo");
                action.activate += redo;

                action = (Action) builder.get_object("action_cut");
                action.activate += cut_selection;

                action = (Action) builder.get_object("action_copy");
                action.activate += copy_selection;

                action = (Action) builder.get_object("action_paste");
                action.activate += paste;

                action = (Action) builder.get_object("action_delete");
                action.activate += delete_selection;

                action = (Action) builder.get_object("action_about");
                action.activate += about;

                mainwindow.show_all();

                pipeline_controller.reset();
            } else {
                stderr.printf("Error loading the ui file\n");
                Gtk.main_quit();
            }
        } catch (GLib.Error e) {
            stderr.printf("%s\n", e.message);
            Gtk.main_quit();
        }

    }

    private void quit_app()
    {
        pipeline_controller.close();
        Gtk.main_quit();
    }

    private void undo()
    {
        stdout.printf("undo\n");
    }

    private void redo()
    {
        stdout.printf("redo\n");
    }

    private void cut_selection()
    {
        stdout.printf("cut_selection\n");
    }

    private void copy_selection()
    {
        stdout.printf("copy_selection\n");
    }

    private void paste()
    {
        stdout.printf("paste\n");
    }

    private void delete_selection()
    {
        stdout.printf("delete_selection\n");
    }

    private void about()
    {
        stdout.printf("about\n");
    }
}

}

