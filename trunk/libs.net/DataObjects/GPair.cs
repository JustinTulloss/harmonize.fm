using System;
using System.Collections.Generic;

namespace DMP
{
	class GPair<T1, T2>
	{
		public T1 First;
		public T2 Second;

		GPair(T1 first, T2 second) {
			this.First = first;
			this.Second = second;
		}
	}
}
