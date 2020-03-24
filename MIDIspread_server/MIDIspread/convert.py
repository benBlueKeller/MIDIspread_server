# from xlrd import open_workbook
from miditime.miditime import MIDITime

# Below line throws error in deployment, change to MIDIspread.sheets
from sheets import get_range


class Convert:
    """Convert turns google sheets into midi with miditime

    Attributes:
        spreadsheet_id (str): id of google sheet
        range (str): sheet range in a1 notation for notes.
            One to four columns can be used (with defaults for missing columns);
            time in first column, pitch in second (or first),
            velocity in third (or 100), duration in fourth (or 1).
        bpm (int): beats per minute for the midi output
        find_time(function): conversion function for time;
            the output will be when a note happens
        find_pitch(function): conversion function for pitch;
            how high or low is it?
        find_velocity(function): conversion function for velocity;
            how stong?
        find_duration(function): conversion function for duration;
            how long?
        miditime(MIDITime instance): from CIR (github.com/cirlabs/miditime);
            initialized on __init__
        data_list(:list: :list: int): list given to miditime.add_track
            in data_to_file; created in sheets_to_data
    """

    def __init__(
        self,
        spreadsheet_id="1YkaCukkp0w-enqqJCDNgjbM3PKimfr6Ic6lo_02PSM0",
        range="periodic!B2:D119",
        bpm=120,
        save_path="midi.mid",
        find_time=lambda ti: ti,
        find_pitch=lambda pi: pi,
        find_velocity=lambda ve=100: ve,
        find_duration=lambda du=1: du,
    ):
        super()
        self.spreadsheet_id = spreadsheet_id
        self.range = range
        self.bpm = bpm
        self.find_time = find_time
        self.find_pitch = find_pitch
        self.find_duration = find_duration
        self.find_velocity = find_velocity

        # (beats per min, output file, sec/year, base octave, octaves in range)
        self.miditime = MIDITime(self.bpm, save_path, 5, 5, 1)
        self.sheets_to_data()

    def get_notelist(self):
        """get_notelist takes self.data_list and the class Convert's modifier functions for
        time, pitch, velocity, and duration then returns a list of notes"""
        notelist = []
        for point in self.data_list:
            if isinstance(point, list):
                notelist.append(
                    [
                        self.find_time(point[0]),
                        self.find_pitch(point[1])
                        if len(point) > 1
                        else self.find_pitch(point[0]),
                        self.find_velocity(point[2])
                        if len(point) > 2
                        else self.find_velocity(),
                        self.find_duration(point[3])
                        if len(point) > 3
                        else self.find_duration(),
                    ]
                )
            else:
                notelist.append(
                    [
                        self.find_time(point),
                        self.find_pitch(point),
                        self.find_velocity(),
                        self.find_duration(),
                    ]
                )
        return notelist

    def sheets_to_data(self):
        def str_range_to_ints(range):
            """str_range_to_ints converts sheet schema to ints.

            range-a list of lists for row in sheets
            assumes all values are integars"""
            new = []
            for row in range:
                ints = []
                for cell in row:
                    ints.append(int(cell))
                new.append(ints)
            return new

        str_range = get_range(self.spreadsheet_id, self.range)
        self.data_list = str_range_to_ints(str_range)
        return self.data_list

    def data_to_file(self):
        self.miditime.add_track(self.get_notelist())
        self.miditime.save_midi()


if __name__ == "__main__":
    """example with periodic table"""
    dataMIDI = Convert(
        find_pitch=lambda pi: 81 - pi * 2, find_velocity=lambda ve: 100 - ve * 4,
    )
    dataMIDI.data_to_file()
