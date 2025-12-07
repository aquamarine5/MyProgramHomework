package org.aquamarine5.brainspark.exp17;

public class People {
    private String major;
    private String name;
    private long id;

    public People(String major, String name, long id) {
        this.major = major;
        this.name = name;
        this.id = id;
    }
    public int love(){
        return 1;
    }
    public boolean love(int a){
        return true;
    }
    public String getName() {
        return name;
    }

    public void setName(String name) {
        this.name = name;
    }
}
