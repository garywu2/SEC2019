def sort_expiration(df):
    df.sort_values(by=['TimePriority'])


def orderTrucks(truck_list):
    truck_list.sort(key=lambda x: x.capacity)


# def resetTrucks(truck_list):
# 	for truck in truck_list:
# 		truck.reset()


def allocate(parcel_list, truck_list):
    avail_truck_list = []
    for parcel in parcel_list:
        avail_trucks = []
        for truck in truck_list:
            if (truck.gettimereturn() + truck.timetodest(parcel.destination) < (parcel.expiry - parcel.arrivetime)):
                if parcel.delicate == True and parcel.refrigerate == True and truck.delicate == True and truck.refrig == True:
                    avail_trucks.append(truck)
                elif (parcel.delicate == True and truck.delicate == True):
                    avail_trucks.append(truck)
                elif (parcel.refrig == True and truck.refrig == True):
                    avail_trucks.append(truck)
                else:
                    avail_trucks.append(truck)
        avail_truck_list.append(avail_trucks)
    orderTrucks(truck_list)
    for truck in truck_list:
        parcel_index = 0
        for parcel in parcel_list:
            possible_time = False
            for return_truck in truck_list:
                if (return_truck.gettimereturn() < parcel.getmaxdeparture(return_truck)):
                    possible_time = True
                if possible_time == False:
                    parcel_list.remove(parcel)
                else:
                    # if(parcel_index >= 0 and parcel_index < len(truck_list) - 1):
                    if (truck in avail_truck_list[parcel_index]):
                        if (truck.destination == parcel.destination or truck.destination == None):
                            if (truck.space > parcel.weight):
                                truck.space = truck.space - parcel.weight
                                parcel.truck = truck
                                if (truck.destination == None):
                                    truck.setdestination(parcel.destination)
                                if (parcel.getmaxdeparture(truck) < truck.departure):
                                    truck.departure = parcel.getmaxdeparture(truck)
                        parcel_index = parcel_index + 1
