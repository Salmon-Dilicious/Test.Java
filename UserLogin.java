import java.util.Scanner;

public class UserLogin {
    public static void main(String[] args) {
        User u = new StudentUser("Flame", "student", "1234");
        Scanner sc = new Scanner(System.in);

        try {
            System.out.print("Username: ");
            String id = sc.nextLine();

            System.out.print("Password: ");
            String pw = sc.nextLine();

            if (u.getUsername().equals(id) && u.checkPassword(pw)) {
                System.out.println("Login success");
                u.showRole();
            } else {
                System.out.println("Login failed");
            }
        } catch (Exception e) {
            System.out.println("Error: " + e.getMessage());
        } finally {
            sc.close();
            System.out.println("System closed");
        }
    }
}

class Person {
    protected String name;

    public Person(String name) {
        this.name = name;
    }
}

class User extends Person {
    private String username;
    private String password;

    public User(String name, String username, String password) {
        super(name);
        this.username = username;
        this.password = password;
    }

    public String getUsername() {
        return username;
    }

    public boolean checkPassword(String pw) {
        return password.equals(pw);
    }

    public void showRole() {
        System.out.println("User: " + name);
    }
}

class StudentUser extends User {
    public StudentUser(String name, String username, String password) {
        super(name, username, password);
    }

    @Override
    public void showRole() {
        System.out.println("Student: " + name);
    }
}