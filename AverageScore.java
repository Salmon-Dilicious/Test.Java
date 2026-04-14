class Student {
    String name;
    int score;

    public Student(String name, int score) {
        this.name = name;
        this.score = score;
    }
}

public class AverageScore {
    public static int findMax(int[] arr) {
        if (arr == null || arr.length == 0) {
            throw new IllegalArgumentException("Array must not be null or empty");
        }
        int max = arr[0];
        for (int i = 1; i < arr.length; i++) {
            if (arr[i] > max) {
                max = arr[i];
            }
        }
        return max;
    }

    public static void addBonus(int[] scores) {
        for (int i = 0; i < scores.length; i++) {
            scores[i] += 5;
        }
    }

    public static void curve(Student s) {
        if (s.score < 60) {
            s.score += 10;
        }
    }

    public static int sum(int[] arr) {
        int total = 0;
        for (int num : arr) {
            total += num;
        }
        return total;
    }

    public static void updateScore(Student s, int newScore) {
        s.score = newScore;
    }

    public static void main(String[] args) {
        int[] scores = {70, 80, 90};
        double average = (double) sum(scores) / scores.length;
        System.out.println("1. The average score is: " + average);

        System.out.println("2. The maximum score is: " + findMax(scores));

        addBonus(scores);
        System.out.print("3. Scores after bonus: ");
        for (int score : scores) {
            System.out.print(score + " ");
        }
        System.out.println();

        Student tom = new Student("Tom", 85);
        System.out.println("4. " + tom.name + ": " + tom.score);

        Student tomLow = new Student("TomLow", 55);
        curve(tomLow);
        System.out.println("5. " + tomLow.name + " after curve: " + tomLow.score);

        int[] mixedScores = {45, 62, 80, 59, 90};
        int passCount = 0;
        for (int score : mixedScores) {
            if (score >= 60) {
                passCount++;
            }
        }
        System.out.println("6. Number of scores >= 60: " + passCount);

        System.out.println("7. Total sum of mixedScores: " + sum(mixedScores));

        Student[] students = {
            new Student("Alice", 92),
            new Student("Bob", 48),
            new Student("Charlie", 76)
        };
        System.out.println("8. Student list:");
        for (Student student : students) {
            System.out.println("   " + student.name + ": " + student.score);
        }

        updateScore(tom, 95);
        System.out.println("9. Tom updated score: " + tom.score);

        int minScore = mixedScores[0];
        for (int i = 1; i < mixedScores.length; i++) {
            if (mixedScores[i] < minScore) {
                minScore = mixedScores[i];
            }
        }
        System.out.println("10. The minimum score is: " + minScore);
    }
}
