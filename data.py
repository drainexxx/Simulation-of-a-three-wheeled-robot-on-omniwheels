import matplotlib.pyplot as plt
import statistics

overall_times = [12.31, 12.27, 13.23,12.18,12.17,12.19,12.26,12.41,12.28,12.28,12.37,12.24,12.27,12.27,12.24,12.47,12.17,12.27,12.17,12.25]

min_distances = [0.11,0.12,0.13,0.18,0.19,0.13,0.12,0.12,0.25,0.09,0.16,0.14,0.11,0.06,0.13,0.15,0.16,0.10,0.05,0.08]

max_distances = [1.99,1.94,1.87,1.84,1.98,1.98,1.99,1.86,1.80,1.87,1.84,1.90,1.86,1.90,1.95,1.90,1.97,1.70,1.87,1.93]

medium_distances = [1.13,0.94,0.65,1.06,1.12,1.09,1.25,1.00,0.86,0.99,0.98,0.81,0.93,0.98,0.78,1.00,1.04,0.64,0.76,0.94]

finish_pos = [1.12,0.7,2.05,1.16,1.28,1.24,0.6,0.97,0.43,0.48,0.66,0.56,1.09,1.17,2.24,1.78,1.1,2.4,2.15,1.61]

print("Общее время минимум: ", min(overall_times))
print("Общее время максимум: ", max(overall_times))
print("Общее время среднее: ", statistics.mean(overall_times))

print("Мин.дистанции минимум: ", min(min_distances))
print("Мин.дистанции максимум: ", max(min_distances))
print("Мин.дистанции среднее: ", statistics.mean(min_distances))

print("Макс.дистанции минимум: ", min(max_distances))
print("Макс.дистанции максимум: ", max(max_distances))
print("Макс.дистанции среднее: ", statistics.mean(max_distances))

print("Ср.дистанции минимум: ", min(medium_distances))
print("Ср.дистанции максимум: ", max(medium_distances))
print("Ср.дистанции среднее: ", statistics.mean(medium_distances))

print("Точность на финише минимум: ", min(finish_pos))
print("Точность на финише максимум: ", max(finish_pos))
print("Точность на финише среднее: ", statistics.mean(finish_pos))

fig, axs = plt.subplots(5)
axs[0].plot(overall_times)
axs[0].set_title("Общее время")
axs[1].plot(min_distances)
axs[1].set_title("Мин.дистанция")
axs[2].plot(max_distances)
axs[2].set_title("Макс.дистанция")
axs[3].plot(medium_distances)
axs[3].set_title("Ср.дистанция")
axs[4].plot(finish_pos)
axs[4].set_title("Точность на финише")
plt.show()