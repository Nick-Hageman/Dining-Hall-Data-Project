import sys
import csv
from datetime import datetime, timedelta

def hawkid():
    return(["nthageman"])

def mIndex(D):
    return((sorted([D[key] for key in D], reverse=True))[[x for x in range(1, len(D)+1) if x > (sorted([D[key] for key in D], reverse=True)[x-1])][0]-1])

def parseRecord(record):
    #Takes a record and splits it into a dictionary with 3 parts: Location, Time, and student ID
    return({'loc':record[2], 'time':datetime.strptime(record[0], "%m/%d/%Y %H:%M"), 'sid':int(record[1])})

def manageWindows(W, event, delta):
    if event['loc'] not in W: #Checks if location is in W yet
        W[event['loc']] = [event]
    elif (event['time']- W[event['loc']][0]['time']) <= delta:    #Append it if it is within the time frame
        W[event['loc']].append(event)
    else:
        #This loop clears out the old events that are outside of the new events time delta
        for occurence in W[event['loc']]:
            if event['time'] - occurence['time'] > delta:
                W[event['loc']] = W[event["loc"]][1:]
        W[event['loc']] = W[event['loc']] + [event]
    return(W[event['loc']])

def newWeek(old, new):
    if len(old) == 0:
        return(True)
    else:
        return(old["time"].strftime("%V") != new["time"].strftime("%V")) #Checks if the new and old events occur within the same week

def endWeek(C, M):
    try: #Using try/except allows the corner case to pass by rather than raising an error
        if len(C) == 0:
            return(M)
        else:
            for sid in M:
                #Adds the mIndex to C[sid] for that week
                M[sid].append(mIndex(C[sid]))
        return(M)
    except:
        return(M)

def dumpOutput(M, header):
    print(header)
    for sid in M:
        print("{:08d}".format(sid) + "," + ", ".join([str(x) for x in M[sid]])) #Print to terminal

def scanMeals(filename='data.csv', wsize=2, W={}, C={}, M={}, header='SID'):
    # First, create a timedelta object instance that reflects the
    # specified window size (expressed in minutes). We'll use this
    # interval to regulat the window size at each dining location.
    delta = timedelta(minutes=wsize) 

    # OK, open the speficied file for reading.
    with open(filename, 'r') as f:
        # We're going to keep track of a few things as we scan the
        # records, including how many weeks of data we read (see
        # newWeek() above, where a new week is defined as starting on
        # or after the following Monday).
        week = 0

        # Also we'll initialize a variable that will always contain
        # the previous record; each time through the loop, we update
        # old to contain the current record. At the outset, old is
        # simply an empty dictionary, since the first record does not
        # have a corresponding previous record.
        old = {}

        # The header will be the first line of our output comma-separated
        # value file, and will label the columns of data. The leftmost
        # column will be the student id for the output record, and it will
        # be followed by a number of weekly m-index values. As we parse
        # the data and encounter a new week, we'll append the date of the
        # first day of the new week to header in order to label the new
        # column of data.
        header = 'SID'

        # Read each row/
        for line in f:
            # Turn the line into a list of three substrings by
            # breaking it apart at the commas, making sure to get rid
            # of any trailing newlines or similar. Use parseRecord()
            # to create the current event, which we'll call new.
            new = parseRecord(line.split(","))
            
            # Does this new record refer to a previously unseen sid?
            # If so, create a new entry for it in M, being sure to pad
            # the value with enough 0's to reflect the m-indexes for
            # the weeks we've already processed (this is what that
            # week counter is for!).
            if new['sid'] not in M:
                M[new['sid']] = [0]*week

            # Before we process this new record, does it represent a
            # new week?
            if newWeek(old, new):
                # Update the header. Each week's date should appear as
                # yyyy-mm-dd, so you'll need to study the strftime()
                # method of the datetime object. Finally, note that
                # header "grows" at the beginning of each new week, so
                # it "leads" data collection.
                header = header + ',' + new["time"].strftime("%m/%d/%Y")

                # Now unless this is the very first record in the
                # file, update the M dictionary values with
                # the cumulative m-indexes for each sid up to this
                # point. Note that the list of M values "grows" at the
                # end of each old week, so it "lags" the header.
                if old != {}:
                    # Accumulate the last week's m-index data and
                    # append it to the corresponding M record.
                    endWeek(C, M)
                    week = week + 1

            # Process the new event by adding it into the appropriate
            # window.  Recall manageWindows() returns the
            # appropriately updated window with the new event, which
            # we can now use to update C.
            window = manageWindows(W, new, delta)

            # Now for each subject j in the updated window, increment
            # both C[new['sid']][j] and C[j][new['sid']] by one, representing
            # the shared meal.

            # First, is new['sid'] in C? If not, initialize.
            if new['sid'] not in C:
                C[new['sid']] = {}

            # Recall window is a list of events, where the last event
            # in the window is the event we are presently processing.
            for j in [event['sid'] for event in window]:
                #print("trying {} {}".format(id, j)) #C[j] must already
                # exist by construction, but is does sid exist in
                # C[j]?
                if new['sid'] not in C[j]:
                    C[j][new['sid']] = 0
                C[j][new['sid']] += 1
                # Now handle the other direction of this meal edge. Is
                # C[new['sid']][j] new?
                if j not in C[new['sid']]:
                    C[new['sid']][j] = 0
                C[new['sid']][j] += 1

            # Update retain current row as old and iterate, reading a
            # new row.
            old = new

    # No more data, so the current week is complete: compute the final
    # m-index values.
    endWeek(C, M)

    # Dump the output.
    dumpOutput(M, header)

######################################################################
# MAKE NO CHANGES BEYOND THIS POINT.
######################################################################
# Allows you to invoke this file from the Unix/Mac command line,
# giving the name of the data file and the desired interval, in
# minutes, as follows:
#    % python hw2soln.py test.csv 3 > output.csv
#
scanMeals()
#if __name__ == '__main__':
#    scanMeals(sys.argv[1], int(sys.argv[2]))
