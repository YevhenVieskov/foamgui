c----------------------------------------------------------------------
      program testo
      implicit double precision (a-h,o-z)
c----------------------------------------------------------------------
c.....Test the order of 2D midpoint-rule surface integral approximation
c     Integrating function fi = cos(x) + sin(x)  along line
c     x=0, from y=0 to y=1, using exact and approximate variable value
c     at face centroid
c----------------------------------------------------------------------
c
      fi(x,y) = cos(x) + cos(y)
c
      open(unit=1,file='ointegral1',form='formatted')
      rewind 1
      write(1,*) '#  dx  sume   sum2   sum4   esume   esum2   esum4'
c
      open(unit=2,file='ointerpol1',form='formatted')
      rewind 2
      write(2,*) '#  dx  fiex   cd2   cd4   ecd2   ecd4'

c
      dly=1.0
      dy=2.0*dly
      x0=0.0
      sumex=1.0+sin(dly)
c
c.....Test 5 levels of discretization: from dy=1 to dy=0.0625
c     by halving the previous spacing
c
      ny=1
      do k=1,6
        dy=0.5*dy
        dx=dy
        sume=0.0
        sum2=0.0
        sum4=0.0
c
c.....Loop over all faces
c
        do i=1,ny
c
c.....Face centroid coordinates
c
          yf=0.5*dy+(i-1)*dy
          xf=0.0
c
c.....X-coordinates of cell centroids on the left and on the right
c     (Y-coordinates same as face coordinate, YF)
c
          x1l=-0.5*dx
          x2l=-1.5*dx
          x1r=0.5*dx
          x2r=1.5*dx
c
c.....Exact variable values at neighbor cell centroids
c
          fi1l=fi(x1l,yf)
          fi2l=fi(x2l,yf)
          fi1r=fi(x1r,yf)
          fi2r=fi(x2r,yf)
c
c.....Exact and approximate variable value at face centroid
c
          fifex=fi(x0,yf)
          fifcd2=0.5*(fi1l+fi1r)
          fifcd4=(9.0*fi1l+9.0*fi1r-fi2l-fi2r)/16.0
c
c.....Compute contribution to the integral from the face "i" using
c     exact variable value at face centroid and 2nd and 4th order CD
c
          sume=sume+fifex*dy
          sum2=sum2+fifcd2*dy
          sum4=sum4+fifcd4*dy
c
        end do
c
c.....Compute errors: exact integral value is 1.0
c
        esume=(sumex-sume)/sumex
        esum2=(sumex-sum2)/sumex
        esum4=(sumex-sum4)/sumex
c
c.....Write results for gnuplot evaluation - integral approximations
c
        write(1,*) dx,sume,sum2,sum4,esume,esum2,esum4
c
        ny=ny*2
      end do
c
c.....Check the order of interpolation to cell face at yf=0.5*dly
c
      dx=1.0
      x0=0.0
      yf=0.5
      do k=1,6
        dx=0.5*dx
c
c.....Coordinates of two neighbor nodes on each side (left and right)
c
        x1l=-0.5*dx
        x2l=-1.5*dx
        x1r=0.5*dx
        x2r=1.5*dx
c
c.....Variable values at the two neighbor nodes on each side 
c     (exact, from analytical function)
c
        fi1l=fi(x1l,yf)
        fi2l=fi(x2l,yf)
        fi1r=fi(x1r,yf)
        fi2r=fi(x2r,yf)
c
c.....Exact and interpolated values at face center
c
        fifex=fi(x0,yf)
        fifcd2=0.5*(fi1l+fi1r)
        fifcd4=(9.0*fi1l+9.0*fi1r-fi2l-fi2r)/16.0
c
c.....Compute errors: (exact - approximation)/exact
c
        ecd2=(fifex-fifcd2)/fifex
        ecd4=(fifex-fifcd4)/fifex        
c
c.....Write results for gnuplot evaluation - interpolation
c
        write(2,*) dx,fifex,fifcd2,fifcd4,ecd2,ecd4
c
      end do
c
      stop
      end
