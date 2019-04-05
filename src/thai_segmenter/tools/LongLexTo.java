/**
 * Licensed under the CC-GNU Lesser General Public License, Version 2.1 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://creativecommons.org/licenses/LGPL/2.1/
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */
 
// LongLexTo: Tokenizing Thai texts using Longest Matching Approach
//   Note: Types: 0=unknown  1=known  2=ambiguous  3=English/digits  4=special characters
//
// Public methods: 
//   1) public LongLexTo(File dictFile);  //Constructor with a dictionary file
//   2) public void addDict(File dictFile);     //Add dictionary (e.g., unknown-word file)
//   3) public void wordInstance(String text);  //Word tokenization
//   4) public void lineInstance(String text);  //Line-break tokenization 
//   4) public Vector getIndexList();
//   5) Iterator's public methods: hasNext, first, next
//
// Author: Choochart Haruechaiyasak
// Last update: 28 March 2006

import java.io.*;
import java.util.*;

public class LongLexTo {

  //Private variables
  private Trie dict;               //For storing words from dictionary
  private LongParseTree ptree;     //Parsing tree (for Thai words)

  //Returned variables
  private Vector indexList;  //List of word index positions
  private Vector lineList;   //List of line index positions
  private Vector typeList;   //List of word types (for word only)
  private Iterator iter;     //Iterator for indexList OR lineList (depends on the call)

  /*******************************************************************/
  /*********************** Return index list *************************/
  /*******************************************************************/
  public Vector getIndexList() {
    return indexList; }

  /*******************************************************************/
  /*********************** Return type list *************************/
  /*******************************************************************/
  public Vector getTypeList() {
    return typeList; }
    
  /*******************************************************************/
  /******************** Iterator for index list **********************/
  /*******************************************************************/
  //Return iterator's hasNext for index list 
  public boolean hasNext() {
    if(!iter.hasNext())
      return false;
    return true;
  }
  
  //Return iterator's first index
  public int first() {
    return 0;
  }
  
  //Return iterator's next index
  public int next() {
    return((Integer)iter.next()).intValue();
  }
  
  /*******************************************************************/
  /********************** Constructor (default) **********************/
  /*******************************************************************/
  public LongLexTo() throws IOException {
    
    dict=new Trie();
    File dictFile=new File("lexitron.txt");
    if(dictFile.exists())
      addDict(dictFile);
    else
      System.out.println(" !!! Error: Missing default dictionary file, lexitron.txt");
    indexList=new Vector();
    lineList=new Vector();
    typeList=new Vector();
    ptree=new LongParseTree(dict, indexList, typeList);
  } //Constructor
    
  /*******************************************************************/
  /************** Constructor (passing dictionary file ) *************/
  /*******************************************************************/
  public LongLexTo(File dictFile) throws IOException {

    dict=new Trie();
    if(dictFile.exists())
      addDict(dictFile);
    else
      System.out.println(" !!! Error: The dictionary file is not found, " + dictFile.getName());
    indexList=new Vector();
    lineList=new Vector();
    typeList=new Vector();
    ptree=new LongParseTree(dict, indexList, typeList);
  } //Constructor
  
  /*******************************************************************/
  /**************************** addDict ******************************/
  /*******************************************************************/
  public void addDict(File dictFile) throws IOException {
   
    //Read words from dictionary
    String line, word, word2;
    int index;
    FileReader fr = new FileReader(dictFile);
    BufferedReader br = new BufferedReader(fr);
    
    while((line=br.readLine())!=null) {
      line=line.trim();
      if(line.length()>0)
        dict.add(line);
    }
  } //addDict
  
  /****************************************************************/
  /************************** wordInstance ************************/
  /****************************************************************/
  public void wordInstance(String text) {

    indexList.clear();
    typeList.clear();    
    int pos, index;
    String word;
    boolean found;
    char ch;

    pos=0;
    while(pos<text.length()) {

      //Check for special characters and English words/numbers
      ch=text.charAt(pos);

      //English
      if(((ch>='A')&&(ch<='Z'))||((ch>='a')&&(ch<='z'))) {
        while((pos<text.length())&&(((ch>='A')&&(ch<='Z'))||((ch>='a')&&(ch<='z'))))
          ch=text.charAt(pos++);
        if(pos<text.length())
          pos--;
        indexList.addElement(new Integer(pos));
        typeList.addElement(new Integer(3));
      }
      //Digits
      else if(((ch>='0')&&(ch<='9'))||((ch>='ð')&&(ch<='ù'))) {
        while((pos<text.length())&&(((ch>='0')&&(ch<='9'))||((ch>='ð')&&(ch<='ù'))||(ch==',')||(ch=='.')))
          ch=text.charAt(pos++);
        if(pos<text.length())
          pos--;
        indexList.addElement(new Integer(pos));
        typeList.addElement(new Integer(3));
      }
      //Special characters
      else if((ch<='~')||(ch=='æ')||(ch=='Ï')||(ch=='“')||(ch=='”')||(ch==',')) {
        pos++;
        indexList.addElement(new Integer(pos));
        typeList.addElement(new Integer(4));
      }
      //Thai word (known/unknown/ambiguous)
      else
        pos=ptree.parseWordInstance(pos, text);
    } //While all text length
    iter=indexList.iterator();
  } //wordInstance
        
  /****************************************************************/
  /************************** lineInstance ************************/
  /****************************************************************/
  public void lineInstance(String text) {

    int windowSize=10; //for detecting parentheses, quotes
    int curType, nextType, tempType, curIndex, nextIndex, tempIndex;
    lineList.clear();
    wordInstance(text);
    int i;
    for(i=0; i<typeList.size()-1; i++) {
      curType=((Integer)typeList.elementAt(i)).intValue();
      curIndex=((Integer)indexList.elementAt(i)).intValue();

      if((curType==3)||(curType==4)) {
      //Parenthesese
      if((curType==4)&&(text.charAt(curIndex-1)=='(')) {
          int pos=i+1;
          while((pos<typeList.size())&&(pos<i+windowSize)) {
      tempType=((Integer)typeList.elementAt(pos)).intValue();
          tempIndex=((Integer)indexList.elementAt(pos++)).intValue();  
      if((tempType==4)&&(text.charAt(tempIndex-1)==')')) {
            lineList.addElement(new Integer(tempIndex));
            i=pos-1;
              break;
          }
        }
        }       
        //Single quote
      else if((curType==4)&&(text.charAt(curIndex-1)=='\'')) {
          int pos=i+1;
          while((pos<typeList.size())&&(pos<i+windowSize)) {
      tempType=((Integer)typeList.elementAt(pos)).intValue();
          tempIndex=((Integer)indexList.elementAt(pos++)).intValue();  
      if((tempType==4)&&(text.charAt(tempIndex-1)=='\'')) {
            lineList.addElement(new Integer(tempIndex));
            i=pos-1;
              break;
          }
        }       
      }
      //Double quote
      else if((curType==4)&&(text.charAt(curIndex-1)=='\"')) {
          int pos=i+1;
          while((pos<typeList.size())&&(pos<i+windowSize)) {
      tempType=((Integer)typeList.elementAt(pos)).intValue();
          tempIndex=((Integer)indexList.elementAt(pos++)).intValue();  
      if((tempType==4)&&(text.charAt(tempIndex-1)=='\"')) {
            lineList.addElement(new Integer(tempIndex));
            i=pos-1;
              break;
          }
        }       
      }       
        else
          lineList.addElement(new Integer(curIndex));
      }
      else {
        nextType=((Integer)typeList.elementAt(i+1)).intValue();
        nextIndex=((Integer)indexList.elementAt(i+1)).intValue();
        if((nextType==3)||
          ((nextType==4)&&((text.charAt(nextIndex-1)==' ')||(text.charAt(nextIndex-1)=='\"')||
                           (text.charAt(nextIndex-1)=='(')||(text.charAt(nextIndex-1)=='\''))))
          lineList.addElement(new Integer(((Integer)indexList.elementAt(i)).intValue()));
        else if((curType==1)&&(nextType!=0)&&(nextType!=4))
          lineList.addElement(new Integer(((Integer)indexList.elementAt(i)).intValue()));
      }
    }
    if(i<typeList.size())
      lineList.addElement(new Integer(((Integer)indexList.elementAt(indexList.size()-1)).intValue()));
    iter=lineList.iterator(); 
  } //lineInstance
  
  /****************************************************************/
  /*************************** Demo *******************************/
  /****************************************************************/
  public static void main(String[] args) throws IOException {
     
    LongLexTo tokenizer=new LongLexTo(new File("lexitron.txt"));
    File unknownFile=new File("unknown.txt");
    if(unknownFile.exists())
      tokenizer.addDict(unknownFile);
    Vector typeList;
    String text="", line, inFileName, outFileName;
    char ch;
    int begin, end, type; 
 
    File inFile, outFile;
    FileReader fr;
    BufferedReader br;
    FileWriter fw;
 
    BufferedReader streamReader = new BufferedReader(new InputStreamReader(System.in)); 
    inFileName = args[0].trim();
    inFile=new File(System.getProperty("user.dir") + "//" + inFileName);
    
    if(inFile.exists()) {
      fr=new FileReader(inFile);
      br=new BufferedReader(fr);

      while((line=br.readLine())!=null) {
        line=line.trim();
        if(line.length()>0) {
          tokenizer.wordInstance(line);
          begin=tokenizer.first();
          int i=0;
          while(tokenizer.hasNext()) {
            end=tokenizer.next();
            System.out.println(line.substring(begin, end));
            begin=end;
          }
          System.out.println("");
        }
    }
    } 
  } //main
}
