# function to simplify W/ & N/ feature statements into single net-positive W/ statement
import func

# Prompt user for string input
print("This function will simplify W/ & N/ features into a single combined W/ statement.")
W = input("W/: ")
N = input("N/: ")
M = input("Models: ")

np_list, np_string = func.feature_rewrite(W, N, M)

print("Final net positive: ", np_string)