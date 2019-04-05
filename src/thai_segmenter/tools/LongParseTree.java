/*
 * Decompiled with CFR 0_123.
 * 
 * Could not load the following classes:
 *  Trie
 */
import java.io.IOException;
import java.util.Vector;

public class LongParseTree {
    private Trie dict;
    private Vector indexList;
    private Vector typeList;
    private Vector frontDepChar;
    private Vector rearDepChar;
    private Vector tonalChar;
    private Vector endingChar;

    public LongParseTree(Trie trie, Vector vector, Vector vector2) throws IOException {
        this.dict = trie;
        this.indexList = vector;
        this.typeList = vector2;
        this.frontDepChar = new Vector();
        this.rearDepChar = new Vector();
        this.tonalChar = new Vector();
        this.endingChar = new Vector();
        this.frontDepChar.addElement("\u0e30");
        this.frontDepChar.addElement("\u0e31");
        this.frontDepChar.addElement("\u0e32");
        this.frontDepChar.addElement("\u0e33");
        this.frontDepChar.addElement("\u0e34");
        this.frontDepChar.addElement("\u0e35");
        this.frontDepChar.addElement("\u0e36");
        this.frontDepChar.addElement("\u0e37");
        this.frontDepChar.addElement("\u0e38");
        this.frontDepChar.addElement("\u0e39");
        this.frontDepChar.addElement("\u0e45");
        this.frontDepChar.addElement("\u0e47");
        this.frontDepChar.addElement("\u0e4c");
        this.frontDepChar.addElement("\u0e4d");
        this.rearDepChar.addElement("\u0e31");
        this.rearDepChar.addElement("\u0e37");
        this.rearDepChar.addElement("\u0e40");
        this.rearDepChar.addElement("\u0e41");
        this.rearDepChar.addElement("\u0e42");
        this.rearDepChar.addElement("\u0e43");
        this.rearDepChar.addElement("\u0e44");
        this.rearDepChar.addElement("\u0e4d");
        this.tonalChar.addElement("\u0e48");
        this.tonalChar.addElement("\u0e49");
        this.tonalChar.addElement("\u0e4a");
        this.tonalChar.addElement("\u0e4b");
        this.endingChar.addElement("\u0e46");
        this.endingChar.addElement("\u0e2f");
    }

    private boolean nextWordValid(int n, String string) {
        if (n == string.length()) {
            return true;
        }
        if (string.charAt(n) <= '~') {
            return true;
        }
        for (int i = n + 1; i <= string.length(); ++i) {
            int n2 = this.dict.contains(string.substring(n, i));
            if (n2 == 1) {
                return true;
            }
            if (n2 != 0) break;
        }
        return false;
    }

    public int parseWordInstance(int n, String string) {
        char c = '\u0000';
        int n2 = -1;
        int n3 = -1;
        int n4 = 0;
        int n5 = -1;
        int n6 = 1;
        n4 = 0;
        for (int i = n + 1; i <= string.length() && n6 != -1; ++i) {
            n6 = this.dict.contains(string.substring(n, i));
            if (n6 != 1) continue;
            n2 = i;
            if (!this.nextWordValid(i, string)) continue;
            n3 = i;
            ++n4;
        }
        if (n >= 1) {
            c = string.charAt(n - 1);
        }
        if (n2 == -1) {
            n5 = n + 1;
            if (this.indexList.size() > 0 && (this.frontDepChar.contains("" + string.charAt(n)) || this.tonalChar.contains("" + string.charAt(n)) || this.rearDepChar.contains("" + c) || (Integer)this.typeList.elementAt(this.typeList.size() - 1) == 0)) {
                this.indexList.setElementAt(new Integer(n5), this.indexList.size() - 1);
                this.typeList.setElementAt(new Integer(0), this.typeList.size() - 1);
            } else {
                this.indexList.addElement(new Integer(n5));
                this.typeList.addElement(new Integer(0));
            }
            return n5;
        }
        if (n3 == -1) {
            if (this.rearDepChar.contains("" + c)) {
                this.indexList.setElementAt(new Integer(n2), this.indexList.size() - 1);
                this.typeList.setElementAt(new Integer(0), this.typeList.size() - 1);
            } else {
                this.typeList.addElement(new Integer(1));
                this.indexList.addElement(new Integer(n2));
            }
            return n2;
        }
        if (this.rearDepChar.contains("" + c)) {
            this.indexList.setElementAt(new Integer(n3), this.indexList.size() - 1);
            this.typeList.setElementAt(new Integer(0), this.typeList.size() - 1);
        } else if (n4 == 1) {
            this.typeList.addElement(new Integer(1));
            this.indexList.addElement(new Integer(n3));
        } else {
            this.typeList.addElement(new Integer(2));
            this.indexList.addElement(new Integer(n3));
        }
        return n3;
    }
}
