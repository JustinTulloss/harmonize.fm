# This is a direct port of the svd recommendation in ruby post found at:
# http://www.igvita.com/2007/01/15/svd-recommendation-system-in-ruby/

import numpy
from numpy import array, dot, transpose, column_stack, c_
from numpy import linalg
from operator import itemgetter

"""
Array is:
Ben, Tom, John, Fred x Season 1, 2,3,4,5,6
"""
users = {1: "Ben", 2: "Tom", 3: "John", 4: "Fred"}
m = array([
    [5,5,0,5],
    [5,0,3,4],
    [3,4,0,3],
    [0,0,5,3],
    [5,4,4,5],
    [5,4,5,5]
])

u, s, vt = linalg.svd(m)
vt = transpose(vt)

u2 = c_[u[:,0], u[:,1]]
v2 = c_[vt[:,0], vt[:,1]]

eig2 =array([
    [s[0],0],
    [0,s[1]]
]) 

bob = array([5,5,0,0,0,5])
bobEmbed = dot(dot(bob, u2), linalg.inv(eig2))

user_sim, count = [], 1

for row in v2:
    user_sim.append((count, dot(transpose(bobEmbed), transpose(row))/ \
        (linalg.norm(row) * linalg.norm(bobEmbed))))
    count = count + 1

# Remove all users that fall below the .90 cosine similarity cutoff
similar_users = sorted(filter(lambda x: x[1]>.9, user_sim), 
    key=itemgetter(1), reverse = True)

for user in similar_users:
    print "%s (ID: %d, Similarity: %0.3f)" % (users[user[0]], user[0], user[1])

similarUserItems = transpose(m[:, similar_users[0][0]-1])
myItems = transpose(bob)

not_seen_yet = []
for i in xrange(0, len(myItems)):
    if myItems[i] == 0 and similarUserItems[i] != 0:
        not_seen_yet.append((i+1, similarUserItems[i]))

print "%s recommends:" % users[similar_users[0][0]]
not_seen_yet = sorted(not_seen_yet, key=itemgetter(1), reverse=True)
for season in not_seen_yet:
    print "\tSeason %d .. I gave it a rating of %d" % season

if len(not_seen_yet) == 0:
    print "We've seen all the same seasons, bugger!"
