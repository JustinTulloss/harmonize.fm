using System;

public class Test {
	static void  Main() {
		
	
		Server testServer = new Server();
		
		testServer.InitializeDb("test.db");
		
		testServer.AddDirectory("C:\\Music");

		//Console.WriteLine("Add returned {0}", result?"true":"false");
	
		string[] strList = testServer.ListDirectories();
		Console.WriteLine("Initial list of added directories:");
		foreach(string line in strList)
			Console.WriteLine("{0}", line);
	
		Console.WriteLine("Updating music...");
		testServer.UpdateMusic();
        
        Console.WriteLine("Listing Songs...");
        string[] songs = testServer.ListSongs();
        foreach (string song in songs)
        {
            Console.WriteLine("{0}", song);
        }

        testServer.RemoveDirectory("C:\\My Music");

		string[] strList2 = testServer.ListDirectories();
		Console.WriteLine("Second list of added directories:");
		foreach(string line in strList2)
			Console.WriteLine("{0}", line);

	}
}
