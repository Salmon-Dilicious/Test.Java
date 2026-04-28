class ProbabilityDefinition {
    // 1. 機率的定義 P(A) = 事件A發生的個數 / 全部可能情況
    public static double calculate(double eventCount, double totalCases) {
        return eventCount / totalCases;
    }
}

class SampleSpace {
    // 2. 樣本空間 S: 所有可能結果的集合
    private int totalCases;
    private String description;

    public SampleSpace(int totalCases, String description) {
        this.totalCases = totalCases;
        this.description = description;
    }

    public int getTotalCases() {
        return totalCases;
    }

    public String getDescription() {
        return description;
    }
}

class Event {
    // 3. 事件 A: 我們關心的事件
    private int eventCount;
    private String eventName;

    public Event(int eventCount, String eventName) {
        this.eventCount = eventCount;
        this.eventName = eventName;
    }

    public int getEventCount() {
        return eventCount;
    }

    public String getEventName() {
        return eventName;
    }
}

class BasicFormula {
    // 4. 基本公式 P(A) = n(A) / n(S)
    public static double calculate(Event a, SampleSpace s) {
        return (double) a.getEventCount() / s.getTotalCases();
    }
}

class ComplementEvent {
    // 5. 補事件 P(A^c) = 1 - P(A)
    public static double calculate(double probA) {
        return 1.0 - probA;
    }
}

class Union {
    // 6. 聯集 P(A∪B) = P(A) + P(B) - P(A∩B)
    public static double calculate(double probA, double probB, double probIntersection) {
        return probA + probB - probIntersection;
    }
}

class Intersection {
    // 7. 交集 P(A∩B) = P(A) * P(B|A)
    public static double calculate(double probA, double probBGivenA) {
        return probA * probBGivenA;
    }
}

class ConditionalProbability {
    // 8. 條件機率 P(A|B) = P(A∩B) / P(B)
    public static double calculate(double probIntersection, double probB) {
        return probIntersection / probB;
    }
}

class IndependentEvent {
    // 9. 獨立事件
    // 判斷 P(A∩B) = P(A) * P(B)
    public static boolean checkIndependenceByIntersection(double probIntersection, double probA, double probB) {
        return Math.abs(probIntersection - (probA * probB)) < 1e-9;
    }

    // 判斷 P(A|B) = P(A)
    public static boolean checkIndependenceByCondition(double probAGivenB, double probA) {
        return Math.abs(probAGivenB - probA) < 1e-9;
    }
}

class BayesTheorem {
    // 10. 貝氏定理 P(A|B) = P(B|A) * P(A) / P(B)
    public static double calculate(double probBGivenA, double probA, double probB) {
        return (probBGivenA * probA) / probB;
    }
}

class TotalProbability {
    // 11. 全機率公式 P(A) = Σ P(A|Bi)P(Bi)
    public static double calculate(double[] probAGivenBi, double[] probBi) {
        double total = 0.0;
        for (int i = 0; i < probBi.length; i++) {
            total += probAGivenBi[i] * probBi[i];
        }
        return total;
    }
}

class SchoolExample {
    // 12. 學校例子
    protected double j; // 建中人數
    protected double b; // 北一女人數
    protected double n; // 總人數

    public SchoolExample(double j, double b, double n) {
        this.j = j;
        this.b = b;
        this.n = n;
    }

    public double probJianZhong() {
        return j / n;
    }

    public double probBeiYi() {
        return b / n;
    }
}

class MutuallyExclusiveUnion extends SchoolExample {
    // 13. 建中或北一女 (互斥事件) P(建中∪北一女) = (J+B)/N
    public MutuallyExclusiveUnion(double j, double b, double n) {
        super(j, b, n);
    }

    public double probUnion() {
        return (j + b) / n;
    }
}

public class ProbabilityAssignment {
    public static void main(String[] args) {
        // 1. 機率定義
        System.out.println("1. 機率定義 P(A): " + ProbabilityDefinition.calculate(50, 100));

        // 2. 樣本空間
        SampleSpace s = new SampleSpace(1000, "抽一位學生，所有學生就是樣本空間");
        System.out.println("2. 樣本空間: " + s.getDescription() + "，總數: " + s.getTotalCases());

        // 3. 事件
        Event a = new Event(150, "抽到建中學生");
        System.out.println("3. 事件: " + a.getEventName() + "，人數: " + a.getEventCount());

        // 4. 基本公式
        double probA = BasicFormula.calculate(a, s);
        System.out.println("4. 基本公式 P(A): " + probA);

        // 5. 補事件
        System.out.println("5. 補事件 P(A^c): " + ComplementEvent.calculate(probA));

        // 6. 聯集
        // 公式: P(A∪B) = P(A) + P(B) - P(A∩B)
        // 計算: P(A∪B) = 0.5 + 0.4 - 0.2 = 0.7
        System.out.println("6. 聯集 P(A∪B): " + Union.calculate(0.53, 0.45, 0.2));
        System.out.println("   計算過程: P(A) + P(B) - P(A∩B) = 0.53 + 0.45 - 0.2 = 0.78");

        // 7. 交集
        // 公式: P(A∩B) = P(A) * P(B|A)
        // 計算: P(A∩B) = 0.6 * 0.35 = 0.21
        System.out.println("7. 交集 P(A∩B): " + Intersection.calculate(0.6, 0.35));
        System.out.println("   計算過程: P(A) * P(B|A) = 0.6 * 0.35 = 0.21");

        // 8. 條件機率
        System.out.println("8. 條件機率 P(A|B): " + ConditionalProbability.calculate(0.3, 0.65));

        // 9. 獨立事件
        System.out.println("9. 獨立事件 P(A∩B)=P(A)P(B): " + IndependentEvent.checkIndependenceByIntersection(0.27, 0.60, 0.45));
        System.out.println("   獨立事件 P(A|B)=P(A): " + IndependentEvent.checkIndependenceByCondition(0.60, 0.60));

        // 10. 貝氏定理
        System.out.println("10. 貝氏定理 P(A|B): " + BayesTheorem.calculate(0.85, 0.20, 0.25));

        // 11. 全機率公式
        double[] pAGivenBi = {0.8, 0.4};
        double[] pBi = {0.6, 0.4};
        System.out.println("11. 全機率公式 P(A): " + TotalProbability.calculate(pAGivenBi, pBi));

        // 12. 學校例子
        SchoolExample school = new SchoolExample(300, 200, 1000);
        System.out.println("12. 學校例子 P(建中): " + school.probJianZhong());
        System.out.println("    學校例子 P(北一女): " + school.probBeiYi());

        // 13. 建中或北一女
        MutuallyExclusiveUnion unionSchool = new MutuallyExclusiveUnion(300, 200, 1000);
        System.out.println("13. 建中或北一女 P(建中∪北一女): " + unionSchool.probUnion());
    }
}