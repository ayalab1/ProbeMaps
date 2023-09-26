class Probe:
    """
    A class for mapping the channel indices of an Omnetics probe to the corresponding channel indices of an Intan headstage.

    Attributes:
        channel_map (list): A list of integers representing the channel indices of the probe from dorsal to ventral and left to right shanks.
        chan_per_shank(list): List of number of channels per shank in the order of shanks
        basepath (str): The basepath for saving the device map file.
        probe_type (str): The type of the probe being used.
        probe_name (str): The name of the specific probe model being used.
        num_shanks (int): The number of shanks in the probe.
        save (bool): A flag indicating whether to save the device map file.
        probe_connector (str): The type of connector used by the probe.

    Methods:
        probeOmnetics2_intan32ch: Maps the channel indices of a 32-channel Omnetics probe to the corresponding channel indices of a 32-channel Intan headstage.
        probeOmnetics2_intan64ch: Maps the channel indices of a 64-channel Omnetics probe to the corresponding channel indices of a 64-channel Intan headstage.
        get_device_map: Returns the device map as a string.

    Example usage:
        Create an instance of the ProbeMapper class with the channel map and other arguments
        channel_map = [1, 8, 2, 7, 3, 6, 4, 5, 9, 16, 10, 15, 11, 14, 12, 13, 17, 24, 18, 23, 19, 22, 20, 21, 25, 32, 26, 31, 27, 30, 28, 29]
        probe_mapper = Probe(channel_map, basepath=r"C:\GitHub\LiddellFieldProject\docs\probes_channel_maps", probe_type="neuronexus", probe_name="xyz model", num_shanks=2, save=True, probe_connector="H64")

        Call the method to get the mapped channel indices
        probe_mapper.probeOmnetics2_intan32ch()

        Author: @Praveen Paudel, 2023
    """

    def __init__(self, channel_map, num_shanks, chan_per_shank, basepath=None, probe_type="neuronexus", probe_name=None, save=False, probe_connector="H32"):
        """
        Initializes a new instance of the ProbeMapper class.

        Args:
            channel_map (list): A list of integers representing the desired channel layout of the probe.
            basepath (str): The basepath for saving the device map file.
            probe_type (str): The type of the probe being used.
            probe_name (str): The name of the specific probe model being used.
            num_shanks (int): The number of shanks in the probe.
            chan_per_shank (list): List of number of channels per shank in the order of shanks
            save (bool): A flag indicating whether to save the device map file.
            probe_connector (str): The type of connector used by the probe.
        """
        self.channel_map = channel_map
        self.basepath = basepath
        self.probe_type = probe_type
        self.probe_name = probe_name
        self.num_shanks = num_shanks
        self.save = save
        self.probe_connector = probe_connector
        self.chan_per_shank = chan_per_shank

        # Define the layout of the 32-channel Intan headstage
        self.intan32ch_preamp = [
            23, 22, 21, 20, 19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8,
            24, 25, 26, 27, 28, 29, 30, 31, 0, 1, 2, 3, 4, 5, 6, 7
        ]
        self.intan32ch_preamp_flipped = self.intan32ch_preamp[::-1]

        # Define the layout of the 64-channel Intan headstage
        self.intan64ch_preamp = [
            46, 44, 42, 40, 38, 36, 34, 32, 30, 28, 26, 24, 22, 20, 18, 16,
            47, 45, 43, 41, 39, 37, 35, 33, 31, 29, 27, 25, 23, 21, 19, 17,
            49, 51, 53, 55, 57, 59, 61, 63, 1, 3, 5, 7, 9, 11, 13, 15,
            48, 50, 52, 54, 56, 58, 60, 62, 0, 2, 4, 6, 8, 10, 12, 14
        ]
        self.intan64ch_preamp_flipped = self.intan64ch_preamp[::-1]

        # Define the omnetics connector layout for neuronexus 32 ch probe.
        # for H32 Connector
        if probe_type == "neuronexus" and probe_connector == "H32":
            self.probe32ch_omnetics = [
                18, 27, 28, 29, 17, 30, 31, 32, 1, 2, 3, 16, 4, 5, 6, 15,
                20, 21, 22, 23, 19, 24, 25, 26, 7, 8, 9, 14, 10, 11, 12, 13
            ]
        else:
            self.probe32ch_omnetics = []  # Update with new values

        # Define the omnetics connector layout for neuronexus 64 ch probe.
        # for H64 Connector
        if probe_type == "neuronexus" and probe_connector == "H64":
            self.probe64ch_omnetics = [
                34,43,44,45,33,46,47,48,17,18,19,32,20,21,22,31,
                42,41,40,35,39,38,37,36,29,28,27,26,30,25,24,23,
                64,62,60,58,56,54,52,50,15,13,11,9,7,5,3,1,
                63,61,59,57,55,53,51,49,16,14,12,10,8,6,4,2
            ]
        else:
            self.probe64ch_omnetics = []  # Update with new values

    def probeOmnetics2_intan32ch(self):
        """
        Maps the channel indices of a 32-channel Omnetics probe to the corresponding channel indices of a 32-channel Intan headstage.

        Returns:
            A string representing the device map.
        """
        # Create a dictionary that maps each channel on the Omnetics probe to its index
        probe_index = {value: index for index, value in enumerate(self.probe32ch_omnetics)}

        # Map the channel indices of the Omnetics probe to the corresponding channel indices of the Intan headstage
        device_channel_indices1 = self.map_channel_indices(self.channel_map, probe_index, self.intan32ch_preamp)
        device_channel_indices2 = self.map_channel_indices(self.channel_map, probe_index, self.intan32ch_preamp_flipped)

        if self.save:
            # Save the device map file for the regular version
            with open(f'{self.basepath}/{self.probe_type}_{self.probe_name}_version1.txt', 'w') as f:
                start = 0
                for i in range(self.num_shanks):
                    end = start + self.chan_per_shank[i]
                    f.write('shank{}: '.format(i+1))
                    f.write(' '.join([str(j) for j in device_channel_indices1[start:end]]) + '\n')
                    start = end 

            # Save the device map file for the flipped version
            with open(f'{self.basepath}/{self.probe_type}_{self.probe_name}_version2.txt', 'w') as f:
                start = 0
                for i in range(self.num_shanks):
                    end = start + self.chan_per_shank[i]
                    f.write('shank{}: '.format(i+1))
                    f.write(' '.join([str(j) for j in device_channel_indices2[start:end]]) + '\n')
                    start = end 
        
        # Return the device map as a string
        device_map = f"Contents of {self.probe_type}_{self.probe_name}_version1.txt:\n"
        for i in range(self.num_shanks):
            start = sum(self.chan_per_shank[:i])
            end = start + self.chan_per_shank[i]
            device_map += f"shank{i+1}: {' '.join([str(j) for j in device_channel_indices1[start:end]])}\n"

        device_map += f"\nContents of {self.probe_type}_{self.probe_name}_version2.txt:\n"
        for i in range(self.num_shanks):
            start = sum(self.chan_per_shank[:i])
            end = start + self.chan_per_shank[i]
            device_map += f"shank{i+1}: {' '.join([str(j) for j in device_channel_indices2[start:end]])}\n"

        print(device_map, end=" ")

    def probeOmnetics2_intan64ch(self):
        """
        Maps the channel indices of a 64-channel Omnetics probe to the corresponding channel indices of a 64-channel Intan headstage.

        Returns:
            A string representing the device map.
        """
        # Create a dictionary that maps each channel on the Omnetics probe to its index
        probe_index = {value: index for index, value in enumerate(self.probe64ch_omnetics)}

        # Map the channel indices of the Omnetics probe to the corresponding channel indices of the Intan headstage
        device_channel_indices1 = self.map_channel_indices(self.channel_map, probe_index, self.intan64ch_preamp)
        device_channel_indices2 = self.map_channel_indices(self.channel_map, probe_index, self.intan64ch_preamp_flipped)

        if self.save:
            # Save the device map file for the regular version
            with open(f'{self.basepath}/{self.probe_type}_{self.probe_name}_version1.txt', 'w') as f:
                start = 0
                for i in range(self.num_shanks):
                    end = start + self.chan_per_shank[i]
                    f.write('shank{}: '.format(i+1))
                    f.write(' '.join([str(j) for j in device_channel_indices1[start:end]]) + '\n')
                    start = end 


            # Save the device map file for the flipped version
            with open(f'{self.basepath}/{self.probe_type}_{self.probe_name}_version2.txt', 'w') as f:
                start = 0
                for i in range(self.num_shanks):
                    end = start + self.chan_per_shank[i]
                    f.write('shank{}: '.format(i+1))
                    f.write(' '.join([str(j) for j in device_channel_indices2[start:end]]) + '\n')
                    start = end 

        # Return the device map as a string
        device_map = f"Contents of {self.probe_type}_{self.probe_name}_version1.txt:\n"
        for i in range(self.num_shanks):
            start = sum(self.chan_per_shank[:i])
            end = start + self.chan_per_shank[i]
            device_map += f"shank{i+1}: {' '.join([str(j) for j in device_channel_indices1[start:end]])}\n"

        device_map += f"\nContents of {self.probe_type}_{self.probe_name}_version2.txt:\n"
        for i in range(self.num_shanks):
            start = sum(self.chan_per_shank[:i])
            end = start + self.chan_per_shank[i]
            device_map += f"shank{i+1}: {' '.join([str(j) for j in device_channel_indices2[start:end]])}\n"

        print(device_map, end=" ")

    def get_device_map(self):
        """
        Returns the device map as a string in the format:
        Contents of <probe_type>_<probe_name>_version1.txt:
        shank1: <channel_indices>
        shank2: <channel_indices>
        ...
        Contents of <probe_type>_<probe_name>_version2.txt:
        shank1: <channel_indices>
        shank2: <channel_indices>
        ...

        Returns:
            A string representing the device map.
        """
        # Call the probeOmnetics2_intan32ch or probeOmnetics2_intan64ch method to get the device map
        if len(self.probe32ch_omnetics) > 0:
            device_map = self.probeOmnetics2_intan32ch()
        elif len(self.probe64ch_omnetics) > 0:
            device_map = self.probeOmnetics2_intan64ch()
        else:
            device_map = ""

        return device_map

    @staticmethod
    def map_channel_indices(channel_map, probe_index, intan_preamp):
        """
        Maps the channel indices of the Omnetics probe to the corresponding channel indices of the Intan headstage.

        Args:
            channel_map (list): A list of integers representing the channel indices of the Omnetics probe.
            probe_index (dict): A dictionary that maps each channel on the Omnetics probe to its index.
            intan_preamp (list): A list representing the layout of the Intan headstage.

        Returns:
            A list of integers representing the mapped channel indices of the Intan headstage.
"""                        
        return [intan_preamp[probe_index[channel_map[i]]] for i in range(len(channel_map))]

