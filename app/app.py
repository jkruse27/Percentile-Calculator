import kivy
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.scrollview import ScrollView
from kivy.uix.gridlayout import GridLayout
from kivy.lang import Builder
from kivy.uix.boxlayout import BoxLayout
from kivy.metrics import dp
from kivy.uix.screenmanager import Screen, ScreenManager
from kivy_garden.matplotlib.backend_kivyagg import FigureCanvasKivyAgg
from kivymd.app import MDApp
from kivymd.uix.datatables import MDDataTable
from haw import weight_score, height_score, haw_score
from haw import get_height_and_weight_plot, get_haw_plot, get_plots

kivy.require('1.8.0')

KV = """
#:kivy 1.0.9

<MainWindow>:
    name: "forms"
    sex: sex.text
    age: age.text
    weight: weight.text
    h: h.text
    __safe_id: [options.__self__]

    GridLayout:
        cols: 1
        rows: 3
        GridLayout:
            cols: 2
            padding: 10, 10
            size_hint: 0.5, 0.5
            Label:
                color: 'black'
                text: "Sex: "
                size_hint: (1, None)
                height: 35
            RelativeLayout:
                pos: self.parent.pos
                size: self.parent.size
                Button:
                    id: sex
                    text: "Male"
                    size_hint: None, None
                    height: 35
                    on_parent: options.dismiss()
                    on_release: options.open(self)

                DropDown:
                    id: options
                    on_select: sex.text = f'{args[1]}'
                    Button:
                        text: 'Male'
                        size_hint: None, None
                        height: 35
                        on_release: options.select('Male')
                    Button:
                        text: 'Female'
                        height: 35
                        size_hint: None, None
                        on_release: options.select('Female')

            Label:
                color: 'black'
                text: "Age: "
                size_hint: (1, None)
                height: 35

            TextInput:
                id: age
                size_hint: (.2, None)
                height: 35
                multiline: False
                text: '12'
                input_filter: 'int'

            Label:
                color: 'black'
                text: "Weight (kg): "
                size_hint: (1, None)
                height: 35

            TextInput:
                id: weight
                size_hint: (.2, None)
                height: 35
                multiline: False
                text: '43.0'
                input_filter: 'float'

            Label:
                color: 'black'
                text: "Height (cm): "
                size_hint: (1, None)
                height: 35

            TextInput:
                id: h
                size_hint: (.2, None)
                height: 35
                multiline: False
                text: '151'
                input_filter: 'int'

        GridLayout:
            cols:1

        GridLayout:
            cols:1
            padding: 10, 10
            size_hint: 0.2, 0.2
            Button:
                text: "Calculate"
                height: 35
                on_release:
                    app.root.current = "results"
                    root.manager.transition.direction = "left"

<ResultsWindow>:
    name: "results"
"""


class MainWindow(Screen):
    pass


class WindowManager(ScreenManager):
    pass


class MyGrid(GridLayout):
    def __init__(self, **kwargs):
        super(MyGrid, self).__init__(**kwargs)
        self.rows = 1
        self.bind(minimum_width=self.setter('width'))


class MyBox(BoxLayout):
    def __init__(self, **kwargs):
        super(MyBox, self).__init__(**kwargs)
        self.orientation = "vertical"
        self.size_hint_x = 1
        self.bind(minimum_width=self.setter('width'))


class ResultsWindow(Screen):
    def change_screen(self, nothing):
        self.manager.current = 'forms'

    def pdf_callback(self, nothing):
        forms = App.get_running_app().root.get_screen('forms')
        sex = forms.sex
        age = int(forms.age)
        weight = float(forms.weight)
        height = int(forms.h)
        fig = get_plots(sex, age, height, weight, figsize=(8.27, 11.69))
        fig.savefig('results.pdf', format='pdf')

    def on_pre_enter(self):
        button = Button(
            text="<",
            size_hint=(0.2, 0.2),
            on_release=self.change_screen
            )
        button2 = Button(
            text="Export to pdf",
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            size_hint=(0.6, 0.2),
            on_release=self.pdf_callback
            )

        grid = MyGrid(size_hint_x=None, col_default_width=500)
        box = MyBox()

        try:
            forms = App.get_running_app().root.get_screen('forms')
            sex = forms.sex
            age = int(forms.age)
            weight = float(forms.weight)
            height = int(forms.h)
            self.data_tables = MDDataTable(
                size_hint=(1.0, 0.5),
                pos_hint={'center_x': 0.5, 'center_y': 0.5},
                column_data=[
                    ("[size=13]Sex[/size]", dp(15)),
                    ("[size=13]Age[/size]", dp(15)),
                    ("[size=13]Height[/size]", dp(15)),
                    ("[size=13]Weight[/size]", dp(15)),
                    ("[size=13]H. percentile[/size]", dp(20)),
                    ("[size=13]W. percentile[/size]", dp(20)),
                    ("[size=13]HaW[/size]", dp(15)),
                ],
                row_data=[(
                 f'[size=13]{sex}[/size]',
                 f'[size=13]{age} Yrs[/size]',
                 f'[size=13]{height}cm[/size]',
                 f'[size=13]{weight}kg[/size]',
                 f'[size=13]{height_score(sex, age, height):.1f}%[/size]',
                 f'[size=13]{weight_score(sex, age, weight):.1f}%[/size]',
                 f'[size=13]{haw_score(sex, age, height, weight):.1f}%[/size]'
                    )]
            )
            box.add_widget(button)
            box.add_widget(self.data_tables)

            scroll = ScrollView(
                do_scroll_y=False,
                pos_hint={"center_y": .5},
                size_hint=(1, 1),
                do_scroll_x=True)
            scroll.add_widget(grid)

            box.add_widget(scroll)

            grid.add_widget(FigureCanvasKivyAgg(
                figure=get_height_and_weight_plot(sex, age, height, weight),
                size_hint=(1, 1)
                ))
            grid.add_widget(FigureCanvasKivyAgg(
                figure=get_haw_plot(sex, age, height, weight),
                size_hint=(1, 1)
                ))
            box.add_widget(button2)

            self.add_widget(box)

        except:
            self.manager.current = 'forms'


kv = Builder.load_string(KV)


class MyMainApp(MDApp):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainWindow(name='forms'))
        sm.add_widget(ResultsWindow(name='results'))

        return sm


if __name__ == "__main__":
    MyMainApp().run()
